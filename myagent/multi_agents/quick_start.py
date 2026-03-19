from agno.agent import Agent
from agno.models.dashscope import DashScope
import os
from dotenv import load_dotenv
from config import model as glm_model

load_dotenv()

agent = Agent(
    model=glm_model
)
agent.print_response("讲个笑话", stream=True)