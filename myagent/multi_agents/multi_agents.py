from agno.agent import Agent
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools

from config import model as glm



researcher = Agent(
    name="researcher",
    model=glm,
    tools=[DuckDuckGoTools],
    instructions=["搜索最新消息"]
)

writer = Agent(
    name="writer",
    model=glm,
    instructions=["基于研究结果撰写报告"]
)

team = Team(
    name="内容创作团队",
    model=glm,
    members=[researcher, writer],
    markdown=True,
    show_members_responses=True,
    add_datetime_to_context=True,
    mode="coordinate",
)

team.print_response("写一篇关于AI趋势的文章", stream=True)