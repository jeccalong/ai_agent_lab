import os
import logging
import time
import re
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage

from langchain.agents import create_agent


# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
DEBUG = True
MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 5


# ---------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("ai_agent_lab")


# ---------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------
def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression provided as a string.
    For demo purposes, uses Python's eval() with basic error handling.
    WARNING: Do not use eval() with untrusted input in production.
    """
    try:
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


def get_current_time(_: str) -> str:
    """Returns the current date and time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def reverse_string(s: str) -> str:
    """Reverses a string."""
    return s[::-1]


def get_weather(date_str: str) -> str:
    """
    Mock weather tool.

    Accepts:
    - 'today' (case-insensitive)
    - 'YYYY-MM-DD'
    """
    raw = (date_str or "").strip().lower()

    if raw in ("today", ""):
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
            return "Error: Date must be 'today' or in YYYY-MM-DD format."
        date = raw

    today = datetime.now().strftime("%Y-%m-%d")
    return "Sunny, 72°F" if date == today else "Rainy, 55°F"



# ---------------------------------------------------------------------
# RETRY (rate-limit friendly)
# ---------------------------------------------------------------------
def invoke_with_retry(executor, payload):
    delay = RETRY_DELAY_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return executor.invoke(payload)
        except Exception as e:
            msg = str(e).lower()
            is_rate_limit = ("too many requests" in msg) or ("429" in msg) or ("rate limit" in msg)

            if is_rate_limit and attempt < MAX_RETRIES:
                logger.warning(f"⏳ Rate limited (attempt {attempt}/{MAX_RETRIES}). Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(int(delay * 2), 60)
                continue

            raise

# ---------------------------------------------------------------------
# AGENT BUILDER (LangGraph-style create_agent)
# ---------------------------------------------------------------------
def build_agent_executor(llm, tools):
    """
    Your create_agent() returns a LangGraph CompiledStateGraph, which expects input state
    with a 'messages' list. It supports 'system_prompt' (NOT 'prompt').
    """
    system_prompt = (
        "You are a professional and succinct AI assistant. Respond clearly and concisely. "
        "Use tools whenever helpful. "
        "For weather: call get_weather directly. If the user says 'today', pass 'today' to get_weather."
    )


    return create_agent(
        llm,                        # 'model' param in signature (BaseChatModel)
        tools,                      # tools list
        system_prompt=system_prompt,
        debug=DEBUG,
    )


def extract_output(result):
    """
    LangGraph agents commonly return a dict with 'messages' as the transcript.
    We'll grab the last AI message content if present.
    """
    if isinstance(result, dict) and "messages" in result and result["messages"]:
        last = result["messages"][-1]
        # BaseMessage objects have .content
        content = getattr(last, "content", None)
        return content if content is not None else str(last)

    # Fallbacks for other result shapes
    if isinstance(result, dict):
        return result.get("output") or result.get("result") or result.get("content") or str(result)

    return str(result)


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main() -> None:
    logger.info("🤖 Python LangChain Agent Starting...")

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("❌ GITHUB_TOKEN not found.")
        return

    logger.info("✅ GITHUB_TOKEN loaded successfully!")

    llm = ChatOpenAI(
        model="openai/gpt-4o",
        temperature=0,
        base_url="https://models.github.ai/inference",
        api_key=token,
    )
    logger.info("🧠 Language model initialized successfully!")

    tools = [
        Tool(
            name="Calculator",
            func=calculator,
            description="Evaluate math expressions provided as strings.",
            return_direct=True,
        ),
        Tool(
            name="get_current_time",
            func=get_current_time,
            description="Get the current date/time as YYYY-MM-DD HH:MM:SS.",
            return_direct=True,
        ),
        Tool(
            name="reverse_string",
            func=reverse_string,
            description="Reverse a string.",
            return_direct=True,
        ),
        Tool(
            name="get_weather",
            func=get_weather,
            description="Mock weather for a date in YYYY-MM-DD format.",
            return_direct=True,
        ),
    ]
    logger.info("🛠️ Tools initialized successfully!")

    agent_executor = build_agent_executor(llm, tools)

    test_queries = [
        "What time is it right now?",
        "What is 25 * 4 + 10?",
        "Reverse the string 'Hello World'",
        "What's the weather like today?",
        "What is the weather for 2023-04-05?",
    ]

    print("\nRunning example queries:\n")

    for query in test_queries:
        print("─" * 50)
        print(f"📝 Query: {query}\n")
        logger.info(f"AI interaction started for query: {query}")

        start = time.time()
        try:
            # ✅ This is the critical change: LangGraph agent expects 'messages'
            payload = {"messages": [HumanMessage(content=query)]}

            result = invoke_with_retry(agent_executor, payload)
            output = extract_output(result)

            elapsed = time.time() - start
            print(f"✅ Result: {output}\n")
            logger.info(f"AI interaction result: {output}")
            logger.info(f"Query response time: {elapsed:.2f} seconds")

        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error: {e}\n")
            logger.error(f"AI interaction error: {e}")
            logger.info(f"Query response time (with error): {elapsed:.2f} seconds")

    print("🎉 Agent demo complete!\n")
    logger.info("🎉 Agent demo complete!")


if __name__ == "__main__":
    main()

