from graph.definition import graph

input_data = {
        "input": "Please provide the latest updates on my account status.",
        "intent": "",
        "execution_trace": [],
        "results": {},
        "retrieved_context": "",
        "user_id": "user_123",
        "session_id": "session_456",
        "context_enrichment_output": {}
    }

    # Run the graph with the input data
output = graph.invoke(input_data)
print("Graph output:", output)

print("\n\n✅ FINAL RESPONSE:")
print(output["results"]["summary"])
