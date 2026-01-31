import os
import inspect

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
        # Tool(
        #     name="Calculator",
        #     func=calculator,
        #     description=(
        #         "Use this tool to evaluate mathematical expressions, "
        #         "such as arithmetic operations (addition, subtraction, multiplication, division), "
        #         "and to solve math problems provided as strings. "
        #         "Use it whenever a calculation or numeric result is required."
        #     ),
        # )
    ]
    print("🛠️ Tools initialized successfully!")

    # Prompt 11: Create agent with Calculator tool and run a test query
    try:
        agent_executor = build_agent_executor(llm, tools)

        test_query = "What time is it right now?"  # <-- Updated query
        print(f"📝 Agent Test Query: {test_query}")

        payloads = [
            {"input": test_query},
            {"query": test_query},
            {"question": test_query},
            {"messages": [{"role": "user", "content": test_query}]},
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
            raise last_error

        print("🤖 Agent Output:")

        if isinstance(result, dict) and "messages" in result and result["messages"]:
            last_msg = result["messages"][-1]
            content = getattr(last_msg, "content", None)
            print(content if content else last_msg)
        else:
            if isinstance(result, dict):
                print(result.get("output") or result.get("result") or result)
            else:
                print(result)

    except Exception as e:
        print(f"❌ Error running agent: {e}")


if __name__ == "__main__":
    main()
