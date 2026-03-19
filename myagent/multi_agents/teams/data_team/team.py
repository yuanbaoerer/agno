"""Data Development Team - Route mode for data engineering tasks."""

from agno.team.team import Team
from multi_agents.config import model
from multi_agents.agents.sql_expert import sql_expert
from multi_agents.agents.etl_engineer import etl_engineer
from multi_agents.agents.data_modeler import data_modeler
from multi_agents.agents.data_quality import data_quality

data_team = Team(
    id="data-team",
    name="Data Development Team",
    mode="route",
    model=model,
    members=[sql_expert, etl_engineer, data_modeler, data_quality],
    instructions=[
        "You are the leader of a data development team.",
        "Route user requests to the most appropriate specialist.",
        "",
        "Team members:",
        "- SQL Expert: SQL writing, query optimization, database operations",
        "- ETL Engineer: Data pipelines, ETL/ELT development, data integration",
        "- Data Modeler: Data warehouse design, dimensional modeling, schema design",
        "- Data Quality: Data validation, quality monitoring, anomaly detection",
        "",
        "Routing rules:",
        "1. SQL queries, optimization, database questions -> SQL Expert",
        "2. Pipelines, data sync, ETL scripts -> ETL Engineer",
        "3. Table design, modeling, schema questions -> Data Modeler",
        "4. Data checks, quality rules, monitoring -> Data Quality",
        "",
        "For complex requests involving multiple domains:",
        "- Coordinate between specialists",
        "- Synthesize their outputs into a coherent solution",
    ],
    show_members_responses=True,
    markdown=True,
    add_datetime_to_context=True,
)

__all__ = ["data_team"]