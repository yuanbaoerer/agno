from agno.models.dashscope import DashScope
from agno.db.postgres import PostgresDb
import os
from dotenv import load_dotenv

load_dotenv()


model=DashScope(
        id=os.getenv("DASHSCOPE_MODEL_ID", "glm-5"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
)