<p align="center">
  <img src="../assets/python_header.png" alt="Python LangChain AI Agent" />
</p>

# Python LangChain AI Agent Lab

This folder contains my finalized Python LangChain agent demo for the AI Agent Lab, along with a small utility script used to check GitHub Models API rate limits.

This README is intended to **extend** the main project README, not duplicate it. It focuses specifically on what lives in this folder and how it fits into the lab requirements.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-8C2053?style=flat-square&logo=python&logoColor=white" />
  <img alt="LangChain" src="https://img.shields.io/badge/LangChain-Agents-8C2053?style=flat-square&logo=langchain&logoColor=white" />
  <img alt="GitHub Models" src="https://img.shields.io/badge/GitHub%20Models-API-8C2053?style=flat-square&logo=github&logoColor=white" />
</p>




---

## Files in this folder

### `app.py`
This is the **final working version** of my LangChain agent demo.

It demonstrates:
- Creating a chat model using GitHub Models
- Defining local tools
- Letting the agent decide when to call those tools
- Handling tool outputs correctly
- Returning a final response to the user

This file replaces earlier test scripts. Any previous `test.py` file was removed once the logic was verified and stabilized.

---

### `rate_limit_probe.py`
A small utility script used to safely check whether the GitHub Models API is currently rate-limiting requests.

- Sends a minimal request
- Avoids burning tokens
- Prints a clear success or rate-limit message

This script is helpful when debugging `429 Too Many Requests` errors during development.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment variable

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_token_here
```

The token is loaded at runtime and is not committed to version control.

---

## Running the agent demo

```bash
python python-langchain/app.py
```

When run successfully, the script executes a set of example queries and logs the full agent execution flow, including:

- user input
- model reasoning
- tool calls
- tool outputs
- final responses

---

## Tools included in the agent

### Calculator
Evaluates basic math expressions.

- Uses `eval()` with restricted built-ins
- Includes basic error handling
- Intended for demo purposes only

---

### get_current_time
Returns the current date and time in the format:

```
YYYY-MM-DD HH:MM:SS
```

---

### reverse_string
Takes a string input and returns the reversed string.

---

### get_weather (MOCK TOOL)
This is a **mock weather tool**, not a real API call.

Behavior:
- If the date is today → returns `Sunny, 72°F`
- Any other valid date → returns `Rainy, 55°F`
- If the input is not in `YYYY-MM-DD` format, the tool returns an error message

This tool exists purely to demonstrate how an agent interprets date-based questions and selects tools. No real weather data is used.

---

## Rate limiting notes

If you encounter a `429 Too Many Requests` error while running `app.py`, it usually means the GitHub Models API rate limit has been reached.

To check before running the agent:

```bash
python python-langchain/rate_limit_probe.py
```

This helps avoid unnecessary debugging when the issue is simply request limits.

