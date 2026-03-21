"""
AgentOS for Data Development Team

Start the AgentOS server:
    fastapi dev os.py
Or:
    python os.py

Access:
    - Control Panel: http://localhost:8000
    - API Docs: http://localhost:8000/docs
    - Config: http://localhost:8000/config
"""

import sys
from pathlib import Path

# Support running directly: python os.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agno.db.postgres import PostgresDb
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb

from multi_agents.config import model, DATABASE_URL
from multi_agents.agents.sql_expert import sql_expert
from multi_agents.agents.etl_engineer import etl_engineer
from multi_agents.agents.data_modeler import data_modeler
from multi_agents.agents.data_quality import data_quality
from multi_agents.teams.data_team import data_team

# ---------------------------------------------------------------------------
# Database for session/memory persistence
# ---------------------------------------------------------------------------

# Option 1: Use PostgreSQL for production
# db = PostgresDb(db_url=DATABASE_URL)

# Option 2: Use SQLite for development (uncomment to use)
from agno.db.sqlite import SqliteDb
db = SqliteDb(db_file="data_dev.db")

# ---------------------------------------------------------------------------
# Configure agents with db for memory/session support
# ---------------------------------------------------------------------------

# Update agents with db for persistence
sql_expert.db = db
sql_expert.update_memory_on_run = True
sql_expert.add_history_to_context = True
sql_expert.num_history_runs = 3

etl_engineer.db = db
etl_engineer.update_memory_on_run = True

data_modeler.db = db
data_modeler.update_memory_on_run = True

data_quality.db = db
data_quality.update_memory_on_run = True

# Update team with db
data_team.db = db
data_team.update_memory_on_run = True

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------

agent_os = AgentOS(
    id="data-dev-os",
    name="Data Development OS",
    description="Data Development Team with SQL, ETL, Modeling and Quality agents",
    agents=[
        sql_expert,
        etl_engineer,
        data_modeler,
        data_quality,
    ],
    teams=[data_team],
)

app = agent_os.get_app()


# ---------------------------------------------------------------------------
# Run Example
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent_os.serve(app="os:app", port=8000, reload=True)