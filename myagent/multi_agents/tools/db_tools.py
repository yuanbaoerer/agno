"""Database tools for data development agents.

Supports PostgreSQL, MySQL, and other databases via SQLAlchemy.
"""

import json
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit
from agno.utils.log import log_debug, logger

try:
    from sqlalchemy import Engine, create_engine, text
    from sqlalchemy.inspection import inspect
    from sqlalchemy.orm import Session, sessionmaker
except ImportError:
    raise ImportError("`sqlalchemy` not installed. Run: pip install sqlalchemy")


class DataDevTools(Toolkit):
    """
    A toolkit for data development tasks.

    Provides tools for:
    - Database exploration (list tables, describe tables)
    - Query execution with safety limits
    - Schema analysis and optimization suggestions
    - Data quality checks

    Args:
        db_url: SQLAlchemy connection URL
        db_engine: Existing SQLAlchemy engine
        schema: Database schema name
        read_only: If True, only allow SELECT queries (default: True)
        max_rows: Maximum rows to return per query (default: 100)
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        db_engine: Optional[Engine] = None,
        schema: Optional[str] = None,
        read_only: bool = True,
        max_rows: int = 100,
        **kwargs,
    ):
        # Build database engine
        _engine: Optional[Engine] = db_engine
        if _engine is None and db_url is not None:
            _engine = create_engine(db_url, pool_pre_ping=True)

        if _engine is None:
            raise ValueError("Either db_url or db_engine must be provided")

        self.db_engine: Engine = _engine
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.db_engine)
        self.schema = schema
        self.read_only = read_only
        self.max_rows = max_rows

        # Register tools
        tools: List[Any] = [
            self.list_tables,
            self.describe_table,
            self.get_table_ddl,
            self.run_query,
            self.analyze_table_stats,
            self.check_data_quality,
            self.suggest_indexes,
        ]

        super().__init__(name="data_dev_tools", tools=tools, **kwargs)

    def _get_table_names(self) -> List[str]:
        """Get list of table names from database."""
        inspector = inspect(self.db_engine)
        if self.schema:
            return inspector.get_table_names(schema=self.schema)
        return inspector.get_table_names()

    def list_tables(self, pattern: Optional[str] = None) -> str:
        """
        List all tables in the database.

        Args:
            pattern: Optional pattern to filter tables (e.g., 'dim_%', 'fact_%')

        Returns:
            JSON string of table names
        """
        try:
            log_debug(f"Listing tables with pattern: {pattern}")
            tables = self._get_table_names()

            if pattern:
                import fnmatch
                tables = [t for t in tables if fnmatch.fnmatch(t.lower(), pattern.lower())]

            return json.dumps(tables, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return f"Error listing tables: {e}"

    def describe_table(self, table_name: str) -> str:
        """
        Get detailed schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            JSON string with column details (name, type, nullable, default, comment)
        """
        try:
            log_debug(f"Describing table: {table_name}")
            inspector = inspect(self.db_engine)
            columns = inspector.get_columns(table_name, schema=self.schema)

            result = []
            for col in columns:
                result.append({
                    "name": col.get("name"),
                    "type": str(col.get("type")),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default")) if col.get("default") else None,
                    "comment": col.get("comment"),
                })

            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error describing table {table_name}: {e}")
            return f"Error describing table {table_name}: {e}"

    def get_table_ddl(self, table_name: str) -> str:
        """
        Get the CREATE TABLE statement for a table.

        Args:
            table_name: Name of the table

        Returns:
            DDL statement or error message
        """
        try:
            log_debug(f"Getting DDL for table: {table_name}")
            inspector = inspect(self.db_engine)

            # Get columns
            columns = inspector.get_columns(table_name, schema=self.schema)
            pk_constraint = inspector.get_pk_constraint(table_name, schema=self.schema)

            ddl_lines = [f"CREATE TABLE {table_name} ("]

            col_defs = []
            for col in columns:
                col_def = f"    {col['name']} {col['type']}"
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                if col.get("default"):
                    col_def += f" DEFAULT {col['default']}"
                col_defs.append(col_def)

            # Add primary key
            if pk_constraint and pk_constraint.get("constrained_columns"):
                pk_cols = ", ".join(pk_constraint["constrained_columns"])
                col_defs.append(f"    PRIMARY KEY ({pk_cols})")

            ddl_lines.append(",\n".join(col_defs))
            ddl_lines.append(");")

            return "\n".join(ddl_lines)
        except Exception as e:
            logger.error(f"Error getting DDL for {table_name}: {e}")
            return f"Error getting DDL: {e}"

    def run_query(self, query: str, limit: Optional[int] = None) -> str:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            limit: Maximum rows to return (default: self.max_rows)

        Returns:
            JSON string with query results
        """
        if self.read_only:
            query_upper = query.strip().upper()
            if not query_upper.startswith(("SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH")):
                return "Error: Only SELECT queries are allowed in read-only mode"

        try:
            log_debug(f"Running query: {query[:100]}...")
            result = self._execute_sql(query, limit=limit or self.max_rows)
            return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Error running query: {e}")
            return f"Error running query: {e}"

    def _execute_sql(self, sql: str, limit: Optional[int] = None) -> List[Dict]:
        """Execute SQL and return results as list of dicts."""
        with self.Session() as sess:
            result = sess.execute(text(sql))
            try:
                if limit:
                    rows = result.fetchmany(limit)
                else:
                    rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
            except Exception:
                return [{"status": "Query executed successfully"}]

    def analyze_table_stats(self, table_name: str) -> str:
        """
        Analyze table statistics: row count, column statistics, NULL percentages.

        Args:
            table_name: Name of the table

        Returns:
            JSON string with table statistics
        """
        try:
            log_debug(f"Analyzing table stats: {table_name}")
            inspector = inspect(self.db_engine)
            columns = inspector.get_columns(table_name, schema=self.schema)

            stats = {"table": table_name, "columns": {}}

            with self.Session() as sess:
                # Get row count
                count_result = sess.execute(text(f"SELECT COUNT(*) as cnt FROM {table_name}"))
                row_count = count_result.scalar()
                stats["row_count"] = row_count

                # Analyze each column
                for col in columns:
                    col_name = col["name"]
                    col_type = str(col["type"]).upper()

                    col_stats = {"type": col_type}

                    # NULL count
                    null_query = f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL"
                    null_count = sess.execute(text(null_query)).scalar()
                    col_stats["null_count"] = null_count
                    col_stats["null_percentage"] = round(null_count / row_count * 100, 2) if row_count > 0 else 0

                    # Distinct count
                    distinct_query = f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}"
                    distinct_count = sess.execute(text(distinct_query)).scalar()
                    col_stats["distinct_count"] = distinct_count

                    # Numeric stats
                    if any(t in col_type for t in ["INT", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC"]):
                        num_query = f"""
                            SELECT MIN({col_name}) as min_val,
                                   MAX({col_name}) as max_val,
                                   AVG({col_name}) as avg_val
                            FROM {table_name}
                            WHERE {col_name} IS NOT NULL
                        """
                        num_result = sess.execute(text(num_query)).fetchone()
                        if num_result:
                            col_stats["min"] = num_result[0]
                            col_stats["max"] = num_result[1]
                            col_stats["avg"] = float(num_result[2]) if num_result[2] else None

                    stats["columns"][col_name] = col_stats

            return json.dumps(stats, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Error analyzing table stats: {e}")
            return f"Error analyzing table stats: {e}"

    def check_data_quality(self, table_name: str, rules: Optional[str] = None) -> str:
        """
        Run data quality checks on a table.

        Args:
            table_name: Name of the table
            rules: Optional JSON string with custom rules

        Returns:
            JSON string with quality check results
        """
        try:
            log_debug(f"Checking data quality for: {table_name}")
            results = {"table": table_name, "checks": []}

            # Default quality checks
            default_checks = [
                {"name": "row_count", "query": f"SELECT COUNT(*) as value FROM {table_name}", "threshold": "> 0"},
                {"name": "duplicate_check", "query": f"SELECT COUNT(*) - COUNT(DISTINCT *) as value FROM {table_name}", "threshold": "= 0"},
            ]

            checks = default_checks
            if rules:
                try:
                    checks = json.loads(rules)
                except json.JSONDecodeError:
                    pass

            with self.Session() as sess:
                for check in checks:
                    try:
                        result = sess.execute(text(check["query"])).scalar()
                        check_result = {
                            "name": check["name"],
                            "value": result,
                            "threshold": check.get("threshold", "N/A"),
                            "status": "PASS" if self._evaluate_threshold(result, check.get("threshold")) else "FAIL"
                        }
                        results["checks"].append(check_result)
                    except Exception as e:
                        results["checks"].append({
                            "name": check["name"],
                            "status": "ERROR",
                            "error": str(e)
                        })

            return json.dumps(results, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Error checking data quality: {e}")
            return f"Error checking data quality: {e}"

    def _evaluate_threshold(self, value: Any, threshold: Optional[str]) -> bool:
        """Evaluate if value meets threshold condition."""
        if not threshold:
            return True

        try:
            if threshold.startswith(">="):
                return float(value) >= float(threshold[2:])
            elif threshold.startswith("<="):
                return float(value) <= float(threshold[2:])
            elif threshold.startswith(">"):
                return float(value) > float(threshold[1:])
            elif threshold.startswith("<"):
                return float(value) < float(threshold[1:])
            elif threshold.startswith("="):
                return float(value) == float(threshold[1:])
        except (ValueError, TypeError):
            pass
        return True

    def suggest_indexes(self, table_name: str, query_pattern: Optional[str] = None) -> str:
        """
        Suggest indexes for a table based on columns and query patterns.

        Args:
            table_name: Name of the table
            query_pattern: Optional query pattern to analyze

        Returns:
            SQL statements for suggested indexes
        """
        try:
            log_debug(f"Suggesting indexes for: {table_name}")
            inspector = inspect(self.db_engine)
            columns = inspector.get_columns(table_name, schema=self.schema)
            pk_constraint = inspector.get_pk_constraint(table_name, schema=self.schema)
            indexes = inspector.get_indexes(table_name, schema=self.schema)

            suggestions = []
            existing_index_cols = set()

            # Collect existing indexed columns
            for idx in indexes:
                for col in idx.get("column_names", []):
                    existing_index_cols.add(col)
            if pk_constraint:
                for col in pk_constraint.get("constrained_columns", []):
                    existing_index_cols.add(col)

            # Suggest indexes for common patterns
            for col in columns:
                col_name = col["name"]
                col_type = str(col["type"]).upper()

                # Skip already indexed columns
                if col_name in existing_index_cols:
                    continue

                # Suggest indexes for foreign key patterns
                if col_name.endswith("_id") or col_name.endswith("_key"):
                    suggestions.append(
                        f"-- Foreign key column\nCREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});"
                    )

                # Suggest indexes for date/timestamp columns
                if any(t in col_type for t in ["DATE", "TIME", "TIMESTAMP"]):
                    suggestions.append(
                        f"-- Date/timestamp column for time-based queries\nCREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});"
                    )

                # Suggest indexes for status/type columns
                if any(name in col_name.lower() for name in ["status", "type", "state", "category"]):
                    suggestions.append(
                        f"-- Low cardinality column for filtering\nCREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});"
                    )

            if not suggestions:
                return f"No additional index suggestions for table {table_name}"

            return "\n".join(suggestions)
        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")
            return f"Error suggesting indexes: {e}"


__all__ = ["DataDevTools"]