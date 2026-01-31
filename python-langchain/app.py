import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from datetime import datetime
from langchain_core.tools import Tool
from langchain.agents import create_agent

def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression provided as a string.
    For demo purposes, uses Python's eval() with basic error handling.
    WARNING: Do not use eval() with untrusted input in production.
    """
    try:
        # Only allow certain built-in functions and operators for safety
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

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

    # Create tools list with Calculator tool
    tools = [
        Tool(
            name="Calculator",
            func=calculator,
            description=(
                "Use this tool to evaluate mathematical expressions, "
                "such as arithmetic operations (addition, subtraction, multiplication, division), "
                "and to solve math problems provided as strings. "
                "Use it whenever a calculation or numeric result is required."
            ),
        )
    ]

    query = "What is 25 * 4 + 10?"
    print(f"📝 Query: {query}")

    response = llm.invoke(query)
    print("🤖 Response:")
    print(response.content)


if __name__ == "__main__":
    main()
