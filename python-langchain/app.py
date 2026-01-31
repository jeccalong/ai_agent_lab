import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from datetime import datetime
from langchain_core.tools import Tool
from langchain.agents import create_agent

def main() -> None:
    print("🤖 Python LangChain Agent Starting...")

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return

    print("✅ GITHUB_TOKEN loaded successfully!")

    llm = ChatOpenAI(
        model="openai/gpt-4o",
        temperature=0,
        base_url="https://models.github.ai/inference",
        api_key=token,
)
    print("🧠 Language model initialized successfully!")

    query = "What is 25 * 4 + 10?"
    print(f"📝 Query: {query}")

    response = llm.invoke(query)
    print("🤖 Response:")
    print(response.content)


if __name__ == "__main__":
    main()
