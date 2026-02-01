import os
import inspect
import time
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate


def invoke_with_retry(executor, payload, max_retries=5):
    """
    Invokes the agent executor with retries for rate limiting / transient failures.
    Uses exponential backoff.
    """
    delay = 1  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            return executor.invoke(payload)
        except Exception as e:
            msg = str(e).lower()
            if "too many requests" in msg or "429" in msg or "rate limit" in msg:
                if attempt == max_retries:
                    raise
                print(f"⏳ Rate limited (attempt {attempt}/{max_retries}). Retrying in {delay}s...\n")
                time.sleep(delay)
                delay = min(delay * 2, 16)
                continue
            raise


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
    """
    Returns the current date and time as a formatted string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def reverse_string(s: str) -> str:
    """
    Reverses a string.
    """
    return s[::-1]


def get_weather(date_str: str) -> str:
    """
    Returns weather information for a given date string in "YYYY-MM-DD" format.
    If the date matches today's date, returns "Sunny, 72°F".
    For all other dates, returns "Rainy, 55°F".
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        if date_str == today:
            return "Sunny, 72°F"
        return "Rainy, 55°F"
    except Exception as e:
        return f"Error retrieving weather: {e}"


def weather_tool_city(city: str) -> str:
    """
    Returns mock weather data for a given city.
    Takes a city name as a string input parameter.
    Returns a mock weather string based on the city name.
    Includes basic error handling.
    """
    try:
        city_clean = city.strip().lower()
        if city_clean == "san francisco":
            return "San Francisco: Foggy, 60°F"
        elif city_clean == "new york":
            return "New York: Sunny, 75°F"
        elif city_clean == "seattle":
            return "Seattle: Rainy, 55°F"
        elif city_clean == "los angeles":
            return "Los Angeles: Sunny, 80°F"
        else:
            return f"{city.strip().title()}: Weather data not available, defaulting to Cloudy, 68°F"
    except Exception as e:
        return f"Error retrieving weather for {city}: {e}"


def file_tool(action_and_content: str) -> str:
    """
    Reads from or writes to a text file using Python's built-in file operations.
    Input should be in the format:
      - "read:<filename>" to read a file
      - "write:<filename>:<content>" to write content to a file
    Returns the file content for reads, or a success message for writes.
    Includes basic error handling.
    """
    try:
        parts = action_and_content.split(":", 2)
        if len(parts) < 2:
            return "Invalid input format. Use 'read:<filename>' or 'write:<filename>:<content>'."
        action, filename = parts[0].strip().lower(), parts[1].strip()
        if action == "read":
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        elif action == "write":
            if len(parts) < 3:
                return "No content provided for write operation."
            content = parts[2]
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {filename}."
        else:
            return "Unknown action. Use 'read' or 'write'."
    except Exception as e:
        return f"FileTool error: {e}"


def web_search_tool(query: str) -> str:
    """
    Simulates web search results for a given query.
    Takes a search query as a string input parameter.
    Returns a mock search result string.
    Includes basic error handling.
    """
    try:
        query_clean = query.strip().lower()
        if "python" in query_clean:
            return "Python is a popular programming language known for its readability and versatility."
        elif "weather" in query_clean:
            return "Web search result: Today's weather is sunny and 72°F."
        elif "news" in query_clean:
            return "Web search result: AI is transforming technology in 2026."
        else:
            return f"No relevant web results found for '{query.strip()}'."
    except Exception as e:
        return f"WebSearchTool error: {e}"


def build_agent_executor(llm, tools):
    """
    Builds an agent executor using create_agent(), adapting to the installed
    LangChain version's function signature.
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are professional and succinct. "
            "Use tools whenever needed. "
            "If asked about the weather 'today', first call get_current_time to get today's date, "
            "then call get_weather with the date formatted as YYYY-MM-DD."
        ),
        ("user", "{input}"),
        # Many tool-calling agents expect this placeholder; harmless if unused.
        ("placeholder", "{agent_scratchpad}"),
    ])

    sig = inspect.signature(create_agent)
    params = sig.parameters

    kwargs = {}

    if "llm" in params:
        kwargs["llm"] = llm
    elif "model" in params:
        kwargs["model"] = llm

    if "tools" in params:
        kwargs["tools"] = tools
    elif "toolkit" in params:
        kwargs["toolkit"] = tools

    if "prompt" in params:
        kwargs["prompt"] = prompt

    if "debug" in params:
        kwargs["debug"] = True
    elif "verbose" in params:
        kwargs["verbose"] = True

    if kwargs:
        try:
            return create_agent(**kwargs)
        except TypeError:
            pass

    attempts = [
        (llm, tools, prompt),
        (tools, llm, prompt),
        (llm, tools),
        (tools, llm),
    ]

    for args in attempts:
        for extra in ({"debug": True}, {"verbose": True}, {}):
            try:
                return create_agent(*args, **extra)
            except TypeError:
                pass

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

    tools = [
        Tool(
            name="Calculator",
            func=calculator,
            description="Evaluates mathematical expressions. Input should be a math expression string.",
        ),
        Tool(
            name="get_current_time",
            func=get_current_time,
            description="Returns the current date and time as 'YYYY-MM-DD HH:MM:SS'.",
        ),
        Tool(
            name="reverse_string",
            func=reverse_string,
            description="Reverses a string. Input should be a single string.",
        ),
        Tool(
            name="get_weather",
            func=get_weather,
            description="Returns weather info for a date string formatted as 'YYYY-MM-DD'.",
        ),
        Tool(
            name="weather_tool_city",
            func=weather_tool_city,
            description="Returns mock weather data for a given city.",
        ),
        Tool(
            name="file_tool",
            func=file_tool,
            description="Reads from or writes to a text file.",
        ),
        Tool(
            name="web_search_tool",
            func=web_search_tool,
            description="Simulates web search results for a given query.",
        ),
    ]
    print("🛠️ Tools initialized successfully!")

    try:
        agent_executor = build_agent_executor(llm, tools)

        test_queries = [
            "What time is it right now?",
            "What is 25 * 4 + 10?",
            "Reverse the string 'Hello World'",
            "What's the weather like today?",
            "What is the weather for 2023-04-05?",
            "What is the weather in San Francisco?",
            "What is the weather in New York?",
            "What is the weather in Seattle?",
            "What is the weather in Los Angeles?",
            "What is the weather in Chicago?",
        ]

        print("\nRunning example queries:\n")

        for query in test_queries:
            print("─" * 50)
            print(f"📝 Query: {query}\n")

            try:
                result = invoke_with_retry(agent_executor, {"input": query})

                if isinstance(result, dict):
                    output = result.get("output") or result.get("result") or result.get("content")
                    if not output and "messages" in result and result["messages"]:
                        last_msg = result["messages"][-1]
                        output = getattr(last_msg, "content", None) or last_msg
                else:
                    output = result

                print(f"✅ Result: {output}\n")

            except Exception as e:
                print(f"❌ Error: {e}\n")

        print("🎉 Agent demo complete!\n")

    except Exception as e:
        print(f"❌ Error running agent: {e}")


if __name__ == "__main__":
    main()

