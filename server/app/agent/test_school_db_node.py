
from app.agent.source_nodes import school_db_node


test_queries = [
    "Show me Aarav Sharma's attendance",
    "Show me Aarav Sharma's fee details",
    "Show me Aarav Sharma's payment history",
    "Which bus is assigned to Aarav Sharma?",
    "Find teacher Kavita Mehta",
]

for query in test_queries:

    print("\n========== SCHOOL DB NODE TEST ==========")
    print("Query:", query)

    result = school_db_node({
        "query": query,
        "tenant_id": "TENANT_001",
        "branch_id": "BRANCH_001",
        "source_results": []
    })

    for item in result["source_results"]:
        print(item)
