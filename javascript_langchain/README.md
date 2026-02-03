<p align="center">
  <img src="../assets/javascript_header.png" alt="JavaScript LangChain AI Agent" />
</p>

# JavaScript LangChain AI Agent Lab (Current State)

This folder contains the **current working version** of the JavaScript LangChain agent demo for the AI Agent Lab.

This README supplement describes the present state of `app.js` and its capabilities, not the projected or final lab requirements.

<p align="center">
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-ES2022+-8C2053?style=flat-square&logo=javascript&logoColor=white" />
  <img alt="Node.js" src="https://img.shields.io/badge/Node.js-18+-8C2053?style=flat-square&logo=node.js&logoColor=white" />
  <img alt="LangChain" src="https://img.shields.io/badge/LangChain-Agents-8C2053?style=flat-square" />
  <img alt="GitHub Models" src="https://img.shields.io/badge/GitHub%20Models-API-8C2053?style=flat-square&logo=github&logoColor=white" />
</p>

---

## Files in this folder

### `app.js`
This is the **current working version** of the JavaScript LangChain agent demo.

It demonstrates:
- Creating a chat model client using GitHub Models
- Defining multiple local tools in JavaScript:
  - **Calculator**: Evaluates math expressions
  - **get_current_time**: Returns the current date in yyyy-MM-dd format
  - **reverse_string**: Reverses a string
  - **get_weather**: Returns mock weather for a given date (multi-function chaining demo)
- Allowing the agent to decide when to call each tool
- Handling tool outputs in an async/await flow
- Returning a final response to the user
- Chaining multiple tool calls automatically (e.g., answering "What's the weather like today?")

---

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Environment variable

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_token_here
```

The token is loaded at runtime and is not committed to version control.

---

## Running the agent demo

From this folder:

```bash
node app.js
```

---

## Tools included in the agent (current state)

### Calculator
Evaluates basic math expressions.

### get_current_time
Returns the current date in yyyy-MM-dd format.

### reverse_string
Reverses a string.

### get_weather
Returns mock weather for a given date (yyyy-MM-dd).
- If the date is today, returns "Sunny, 72°F"
- Otherwise, returns "Rainy, 55°F"
- Demonstrates multi-function chaining: the agent can call get_current_time, then get_weather, to answer questions like "What's the weather like today?"

---

## Example queries

- What time is it right now?
- What is 25 * 4 + 10?
- Reverse the string 'Hello World'
- What's the weather like today? (triggers multi-function chaining)

---

## Rate limiting notes

If you encounter a `429 Too Many Requests` error while running the JavaScript agent, it means the GitHub Models API rate limit has been reached.

The current implementation does not include retry or cooldown logic. You must wait for the rate limit to reset before running more queries.

---

## License

Educational use only.
