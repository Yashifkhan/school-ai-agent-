
from app.agent.response_node import response_node


test_state = {
    "query": "Show me Aarav Sharma's fee details",

    "source_results": [
        {
            "source": "school_db",
            "status": "success",
            "action": "fees",
            "student_id": "STU001",
            "student_name": "Aarav Sharma",
            "data": [
                {
                    "total_amount": 3500,
                    "amount_paid": 2000,
                    "balance_due": 1500,
                    "status": "partially_paid"
                }
            ]
        }
    ]
}


result = response_node(test_state)

print("\n========== FINAL ANSWER ==========\n")
print(result["final_answer"])
