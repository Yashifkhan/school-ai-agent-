
# from app.agent.graph import agent_graph


# TENANT_ID = "TENANT_001"
# BRANCH_ID = "BRANCH_001"


# test_queries = [
#     "Show me Aarav Sharma's attendance",
#     "Show me Aarav Sharma's fee details",
#     "Show me Aarav Sharma's payment history",
#     "Which bus is assigned to Aarav Sharma?",
#     "Find teacher Kavita Mehta",
# ]


# for query in test_queries:

#     print("\n" + "=" * 60)
#     print("USER QUERY:", query)

#     initial_state = {
#         "query": query,
#         "tenant_id": TENANT_ID,
#         "branch_id": BRANCH_ID,
#         "source_results": []
#     }

#     try:

#         result = agent_graph.invoke(initial_state)

#         print("\nCLASSIFICATION:")
#         print(result.get("classification"))

#         print("\nSOURCE RESULTS:")

#         for item in result.get("source_results", []):
#             print(item)

#     except Exception as error:

#         print("\nGRAPH EXECUTION FAILED:")
#         print(type(error).__name__, error)



from app.agent.graph import agent_graph

initial_state = {
    "query": "Show me Aarav Sharma's fee details",
    "tenant_id": "TENANT_001",
    "branch_id": "BRANCH_001",
    "source_results": []
}

result = agent_graph.invoke(initial_state)

print("\n========== CLASSIFICATION ==========")
print(result.get("classification"))

print("\n========== SOURCE RESULTS ==========")
print(result.get("source_results"))

print("\n========== FINAL ANSWER ==========")
print(result.get("final_answer"))