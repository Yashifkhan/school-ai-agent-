
from app.agent.graph import agent_graph


# queries = [

#     "What is a school ERP?",

#     "How do I register a new student in our software?",

#     "Show me attendance for student Rahul.",

#     "What are the latest CBSE guidelines?",

#     "Explain the latest CBSE guidelines and "
#     "how our school software manages attendance."
# ]


# for query in queries:

#     print("\n" + "=" * 60)
#     print("USER QUERY:", query)

#     result = agent_graph.invoke({

#         "query": query,

#         "classification": None,

#         "source_results": []

#     })

#     print("\nCLASSIFICATION:")

#     print(
#         result["classification"].model_dump_json(indent=2)
#     )

#     print("\nROUTING RESULTS:")

#     for item in result["source_results"]:
#         print(item)



# result = agent_graph.invoke({
#     "query": "What is a school ERP and why do schools use it?",
#     "classification": None,
#     "source_results": []
# })

# print("\n========== FINAL SOURCE RESULTS ==========")

# for item in result["source_results"]:
#     print("\nSource:", item["source"])
#     print("Status:", item["status"])
#     print("Answer:", item.get("content"))






import asyncio

from app.agent.graph import agent_graph


async def main():

    query = (
        "What are the latest official CBSE "
        "guidelines for school attendance?"
    )

    result = await agent_graph.ainvoke({

        "query": query,

        "classification": None,

        "source_results": []

    })

    print("\n========== CLASSIFICATION ==========")

    print(
        result["classification"].model_dump_json(indent=2)
    )

    print("\n========== SOURCE RESULTS ==========")

    for item in result["source_results"]:

        print("\nSOURCE:", item["source"])

        print("STATUS:", item["status"])

        if item["source"] == "web_search":

            content = item["content"]

            print("QUERY:", content["query"])

            print("RESPONSE TIME:", content["response_time"])

            for index, search_result in enumerate(
                content["results"], start=1
            ):

                print(f"\nRESULT {index}")

                print("TITLE:", search_result["title"])

                print("URL:", search_result["url"])

                print("SCORE:", search_result["score"])

                print("CONTENT:", search_result["content"])


if __name__ == "__main__":

    asyncio.run(main())










# from app.tools.llm_knowledge import answer_general_question


# query = "What is a school ERP and why do schools use it?"


# answer = answer_general_question(query)


# print("\n========== LLM KNOWLEDGE RESULT ==========\n")

# print(answer)




# import asyncio

# from app.tools.web_search import search_web


# async def main():

#     query = (
#         "Latest official CBSE guidelines "
#         "for school attendance in India"
#     )

#     print("\n========== WEB SEARCH TEST ==========\n")

#     response = await search_web(
#         query=query,
#         max_results=3,
#         search_depth="fast",
#         topic="general",
#     )

#     print("QUERY:", response.query)

#     print("\nRESPONSE TIME:", response.response_time)

#     print("\nTOTAL RESULTS:", len(response.results))

#     print("\n========== SEARCH RESULTS ==========\n")

#     for index, result in enumerate(response.results, start=1):

#         print(f"\nRESULT {index}")

#         print("TITLE:", result.title)

#         print("URL:", result.url)

#         print("SCORE:", result.score)

#         print("CONTENT:", result.content)

#     print("\n========== COMPLETE ==========\n")


# if __name__ == "__main__":

#     asyncio.run(main())
