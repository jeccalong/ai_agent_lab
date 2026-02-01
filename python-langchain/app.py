"""
Python LangChain AI Agent (Lab)

Goals:
- Load GitHub Models token from .env
- Create a ChatOpenAI client against GitHub Models
- Define simple tools (calculator, time/date, reverse string, mock weather)
- Run a few example queries through a tool-calling agent
- Be resilient to GitHub Models rate limiting (HTTP 429 / "Too many requests")
- Avoid accidentally spamming the API (DRY_RUN + minimal payload attempts)

Notes:
- This is a student lab demo. The calculator uses eval() with a restricted environment
  and is NOT production-safe.
"""

import os
import time
import inspect
import logging
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent

# Optional memory (not all LangChain agent builders support it)
try:
    from langchain_community.memory import ConversationBufferMemory
except Exception:
    ConversationBufferMemory = None

# ---------------------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ai_agent_lab")

# ---------------------------------------------------------------------
# SAFETY / COST CONTROLS
# ---------------------------------------------------------------------

# Set to True to prevent any API calls (HIGHLY recommended while rate-limited).
DRY_RUN = True

# Keep retries low to avoid hammering the API when hard-limited.
MAX_RETRIES = 2

# Toggle debug/verbose logs. Debug output can increase token usage.
DEBUG = False


# ---------------------------------------------------------------------
# RETRY / RATE LIMIT HANDLING
# ---------------------------------------------------------------------

def invoke_with_retry(executor, payload, max_retries=MAX_RETRIES):
    """
    Invoke the agent executor with limited retries for transient failures.

    Why limited retries?
    - If you are hard rate-limited, repeated retries waste requests.
    - We retry only a small number of times, then fail fast with a clear message.
    """
    delay_seconds = 2

    for attempt in range(1, max_retries + 1):
        try:
            return executor.invoke(payload)
        except Exception as e:
            msg = str(e).lower()
            is_rate_limit = ("too many requests" in msg) or ("429" in msg) or ("rate limit" in msg)

            if is_rate_limit and attempt < max_retries:
                print(f"⏳ Rate limited (attempt {attempt}/{max_retries}). Retrying in {delay_seconds}s...\n")
                time.sleep(delay_seconds)
                delay_seconds = min(delay_seconds * 2, 16)
                continue

            if is_rate_limit:
                raise RuntimeError(
                    "Rate limited by GitHub Models (HTTP 429). "
                    "Stop running the script and try again later."
                ) from e

            raise


# ---------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------

def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression provided as a string.
    """
    logger.info(f"Calculator tool called with: {expression}")
    try:
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names, {})
        logger.info(f"Calculator result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return f"Error evaluating expression: {e}"


def get_current_time(_: str) -> str:
    """
    Returns the current date and time in YYYY-MM-DD HH:MM:SS format.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"get_current_time tool called. Returning: {now}")
    return now


def get_current_date(_: str) -> str:
    """
    Returns today's date in YYYY-MM-DD format.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"get_current_date tool called. Returning: {today}")
    return today


def reverse_string(s: str) -> str:
    """
    Reverses a string using Python slice notation.
    """
    logger.info(f"reverse_string tool called with: {s}")
    reversed_str = s[::-1]
    logger.info(f"reverse_string result: {reversed_str}")
    return reversed_str


def get_weather(date_str: str) -> str:
    """
    Mock weather tool.
    """
    logger.info(f"get_weather tool called with: {date_str}")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        result = "Sunny, 72°F" if date_str == today else "Rainy, 55°F"
        logger.info(f"get_weather result: {result}")
        return result
    except ValueError:
        logger.error("get_weather error: invalid date format")
        return "Error retrieving weather: invalid date format (expected YYYY-MM-DD)."
    except Exception as e:
        logger.error(f"get_weather error: {e}")
        return f"Error retrieving weather: {e}"


# ---------------------------------------------------------------------
# AGENT BUILDER (signature-adaptive)
# ---------------------------------------------------------------------

def build_agent_executor(llm, tools, memory=None):
    """
    Builds an agent executor using create_agent(), adapting to the installed
    LangChain version's create_agent() signature.

    Key point:
    - Your environment's create_agent() does NOT accept kwarg 'llm'.
      It may accept 'model' instead, or require positional args.
    - Some versions do NOT accept 'memory' either, so we only pass it if supported.
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a professional, succinct AI assistant. "
            "Use tools whenever they are needed for accuracy. "
            "If asked about weather 'today', first call get_current_date, "
            "then call get_weather with the date formatted as YYYY-MM-DD."
        ),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    sig = inspect.signature(create_agent)
    params = list(sig.parameters.keys())

    # -------------------------
    # 1) Try keyword-based call
    # -------------------------
    kwargs = {}

    # Model parameter name differs across versions
    if "llm" in params:
        kwargs["llm"] = llm
    elif "model" in params:
        kwargs["model"] = llm

    # Tools parameter name differs across versions
    if "tools" in params:
        kwargs["tools"] = tools
    elif "toolkit" in params:
        kwargs["toolkit"] = tools

    # Prompt optional
    if "prompt" in params:
        kwargs["prompt"] = prompt

    # Memory optional (only pass if supported)
    if memory is not None and "memory" in params:
        kwargs["memory"] = memory

    # Debug/verbose optional
    if "debug" in params:
        kwargs["debug"] = DEBUG
    elif "verbose" in params:
        kwargs["verbose"] = DEBUG

    if kwargs:
        try:
            return create_agent(**kwargs)
        except TypeError:
            # If keyword mapping doesn't match, fall back to positional attempts.
            pass

    # -------------------------
    # 2) Positional call attempts
    # -------------------------
    # Common patterns in older/newer builds:
    candidates = [
        (llm, tools, prompt),
        (tools, llm, prompt),
        (llm, tools),
        (tools, llm),
        (llm,),
        (tools,),
    ]

    for args in candidates:
        # Try passing debug/verbose only if the signature supports it.
        if "debug" in params:
            try:
                return create_agent(*args, debug=DEBUG)
            except TypeError:
                pass
        if "verbose" in params:
            try:
                return create_agent(*args, verbose=DEBUG)
            except TypeError:
                pass

        try:
            return create_agent(*args)
        except TypeError:
            pass

    raise TypeError(f"Could not construct agent with create_agent(). Signature is: {sig}")


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main() -> None:
    logger.info("🤖 Python LangChain Agent Starting...")

    if DRY_RUN:
        logger.warning("🚫 DRY_RUN is enabled — no API calls will be made.")
        return

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        logger.error("❌ GITHUB_TOKEN not found.")
        print("   Create a .env file in your project root with:")
        print("   GITHUB_TOKEN=your_token_here")
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
            description="Evaluates a math expression string (e.g., '25 * 4 + 10').",
        ),
        Tool(
            name="get_current_time",
            func=get_current_time,
            description="Returns current date and time as 'YYYY-MM-DD HH:MM:SS'.",
        ),
        Tool(
            name="get_current_date",
            func=get_current_date,
            description="Returns today's date as 'YYYY-MM-DD'.",
        ),
        Tool(
            name="reverse_string",
            func=reverse_string,
            description="Reverses a string. Input should be a single string.",
        ),
        Tool(
            name="get_weather",
            func=get_weather,
            description="Returns mock weather for a date string formatted 'YYYY-MM-DD'.",
        ),
    ]
    logger.info("🛠️ Tools initialized successfully!")

    memory = None
    if ConversationBufferMemory is not None:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent_executor = build_agent_executor(llm, tools, memory=memory)

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

        try:
            result = invoke_with_retry(agent_executor, {"input": query})

            output = None
            if isinstance(result, dict):
                output = result.get("output") or result.get("result") or result.get("content")
                if not output and "messages" in result and result["messages"]:
                    last_msg = result["messages"][-1]
                    output = getattr(last_msg, "content", None) or last_msg
            else:
                output = result

            print(f"✅ Result: {output}\n")
            logger.info(f"AI interaction result: {output}")

        except Exception as e:
            print(f"❌ Error: {e}\n")
            logger.error(f"AI interaction error: {e}")

    print("🎉 Agent demo complete!\n")
    logger.info("🎉 Agent demo complete!")


if __name__ == "__main__":
    main()

