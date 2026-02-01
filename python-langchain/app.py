import os
import inspect
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.agents import create_agent


def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression provided as a string.
    For demo purposes, uses Python's eval() with basic error handling.
    WARNING: Do not use eval() with untrusted input in production.
    """
    try:
        # Restrict eval to prevent access to builtins (demo safety measure)
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


def get_current_time(_: str) -> str:
    """
    Returns the current date and time as a formatted string.
    Uses datetime.now().strftime("%Y-%m-%d %H:%M:%S").
    The input parameter is required by the Tool interface but is not used.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def reverse_string(s: str) -> str:
    """
    Reverses a string.
    Takes a string input parameter and returns the reversed string using Python slice notation [::-1].
    """
    return s[::-1]


def build_agent_executor(llm, tools):
    """
    Builds an agent executor using create_agent(), adapting to the installed
    LangChain version's function signature.
    """
    sig = inspect.signature(create_agent)
    params = sig.parameters

    # Try keyword-based construction if possible (varies by version)
    kwargs = {}

    if "llm" in params:
        kwargs["llm"] = llm
    elif "model" in params:
        kwargs["model"] = llm

    if "tools" in params:
        kwargs["tools"] = tools
    elif "toolkit" in params:
        kwargs["toolkit"] = tools

    # Debug/verbose flag also varies by version
    if "debug" in params:
        kwargs["debug"] = True
    elif "verbose" in params:
        kwargs["verbose"] = True

    if kwargs:
        try:
            return create_agent(**kwargs)
        except TypeError:
            # Fall back to positional attempts below
            pass

    # Positional fallbacks (order differs by version)
    attempts = [
        (llm, tools),
        (tools, llm),
    ]

    for args in attempts:
        # Try with debug
        try:
            return create_agent(*args, debug=True)
        except TypeError:
            pass

        # Try with verbose
        try:
            return create_agent(*args, verbose=True)
        except TypeError:
            pass

        # Try without flags
        try:
            return create_agent(*args)
        except TypeError:
            pass

    # If we got here, we couldn't match the signature
    raise TypeError(f"Could not construct agent with create_agent(). Signature: {sig}")


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

    # Prompt 10: Create tools list with Calculator tool
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
        ),
        Tool(
            name="get_current_time",
            func=get_current_time,
            description=(
                "Use this tool to get the current date and time. "
                "Use it whenever a user asks for the current time or date."
            ),
        ),
        Tool(
            name="reverse_string",
            func=reverse_string,
            description="Reverses a string. Input should be a single string.",
        ),
    ]
    print("🛠️ Tools initialized successfully!")

    # Prompt 11: Create agent with Calculator tool and run a test query
    try:
        agent_executor = build_agent_executor(llm, tools)

        test_queries = [
            "What time is it right now?",
            "What is 25 * 4 + 10?",
            "Reverse the string 'Hello World'",
        ]

        print("\nRunning example queries:\n")

        for query in test_queries:
            print(f"📝 Query: {query}")
            print("─" * 50)

            # Try common input payload shapes (LangChain-version dependent)
            payloads = [
                {"input": query},
                {"query": query},
                {"question": query},
                {"messages": [{"role": "user", "content": query}]},
            ]

            result = None
            last_error = None

            for payload in payloads:
                try:
                    result = agent_executor.invoke(payload)
                    break
                except Exception as e:
                    last_error = e

            if result is None:
                print(f"❌ Error: {last_error}\n")
                continue

            # Extract final output robustly
            output = None
            if isinstance(result, dict):
                output = result.get("output") or result.get("result") or result.get("content")
                if not output and "messages" in result and result["messages"]:
                    last_msg = result["messages"][-1]
                    output = getattr(last_msg, "content", None) or last_msg
            else:
                output = result

            print(f"✅ Result: {output}\n")

        print("🎉 Agent demo complete!")

    except Exception as e:
        print(f"❌ Error running agent: {e}")


if __name__ == "__main__":
    main()
