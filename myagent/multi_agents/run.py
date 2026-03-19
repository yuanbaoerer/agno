"""
Data Development Team Entry Point

Run the data development team with example queries.

Usage:
    python -m multi_agents.run
"""

from multi_agents.teams.data_team import data_team


def main():
    """Run the data development team with test cases."""
    test_cases = [
        "帮我写一个SQL，查询过去7天每个用户的订单数量和金额",
        "设计一个订单事实表，需要支持按日期、用户、商品维度分析",
        "如何监控数据质量？帮我设计一套数据质量检查方案",
        "帮我写一个Airflow DAG，每天增量同步MySQL数据到数据仓库",
    ]

    for idx, prompt in enumerate(test_cases, start=1):
        print(f"\n{'='*60}")
        print(f"Test Case {idx}/{len(test_cases)}")
        print(f"Prompt: {prompt}")
        print("="*60)
        data_team.print_response(prompt, stream=True)


if __name__ == "__main__":
    main()