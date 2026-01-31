from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

import os




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


if __name__ == "__main__":
    main()
