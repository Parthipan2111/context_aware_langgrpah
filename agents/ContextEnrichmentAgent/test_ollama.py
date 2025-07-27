from langchain_openai.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="openhermes",
    base_url="http://localhost:11434/v1",  # Ollama API endpoint
)

response = llm.invoke("How is the weather today?")
print(response.content)
