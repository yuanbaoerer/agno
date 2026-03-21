"""
Shared configuration for multi-agents.

Models, database connections, and other shared settings.
"""

from agno.models.dashscope import DashScope
from dotenv import load_dotenv
import os

load_dotenv()

# Default model for all agents
model = DashScope(
    id=os.getenv("DASHSCOPE_MODEL_ID", "glm-5"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)

# Model for complex reasoning tasks
reasoning_model = DashScope(
    id=os.getenv("DASHSCOPE_REASONING_MODEL_ID", "qwen3.5-plus"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)

# Database configuration
# Support: postgresql://, mysql://, sqlite://, etc.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")

def get_db_tools():
    """Get database tools instance."""
    from multi_agents.tools.db_tools import DataDevTools
    return DataDevTools(db_url=DATABASE_URL, read_only=True, max_rows=100)