"""ETL Engineer Agent - Data pipeline and ETL development."""

import sys
from pathlib import Path

# Support running directly: python agents/etl_engineer/agent.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from agno.agent.agent import Agent
from multi_agents.config import model

etl_engineer = Agent(
    id="etl-engineer",
    name="ETL Engineer",
    model=model,
    instructions=[
        "You are an EL/ETL engineer specializing in data pipeline development.",
        "",
        "Your capabilities:",
        "- Design and implement ETL/ELT pipelines",
        "- Write data transformation scripts (Python, SQL, Spark)",
        "- Create Airflow DAGs and scheduling logic",
        "- Handle data synchronization between systems",
        "- Implement incremental data loading strategies",
        "",
        "Common tools and frameworks you work with:",
        "- Apache Airflow, DolphinScheduler",
        "- Spark, Flink",
        "- Python (pandas, pyarrow)",
        "- Kafka, Debezium for CDC",
        "",
        "When designing pipelines:",
        "1. Consider data freshness requirements",
        "2. Implement proper error handling and retries",
        "3. Add data validation checkpoints",
        "4. Design for idempotency when possible",
        "",
        "Output format:",
        "- Provide code/SQL for the pipeline",
        "- Explain the data flow",
        "- Mention scheduling and dependency considerations",
    ],
    markdown=True,
)

if __name__ == "__main__":
    etl_engineer.print_response(
        """介绍下以下包含的技术内容:
1.打造业界领先的EB级数据处理引擎，并支撑公司内部数据业务迭代发展
2.通过云原生技术栈搭建多云多地域的混合计算底座，完成混合云百万核的资源高效利用，参与Ray/Spark在K8S上的弹性/潮汐资源集群稳定性/可观测性/平台化对接等能力建设
3.支撑公司内部离线ETL，机器学习等业务场景，持续完善Spark/Feature Store/Ray 内核功能及性能.
职位要求
1.良好 Python/C++/Go/Java/Scala等编程基础;
2.具有Ray内核或者Ray 相关框架应用经验者优先;
3.熟悉常见的分布式计算框架(如Spark/Flink等)，有机器学习相关背景优先。
4.有数据平台研发，k8s研发经验者优先""", stream=True
    )


__all__ = ["etl_engineer"]