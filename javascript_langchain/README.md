<p align="center">
  <img src="../assets/javascript_header.png" alt="JavaScript LangChain AI Agent" />
</p>

# JavaScript LangChain AI Agent (Lab)

This project is a **student lab demo** that explores how to build a simple tool-calling AI agent using **LangChain (JavaScript)** and **GitHub Models**. It was completed as part of the [Code:You](https://code-you.org/) AI course curriculum.

The goal of this lab is to understand:
- how agents differ from simple chat completions
- how tools are defined and invoked in JavaScript
- how to safely integrate an external LLM API from Node.js
- how to avoid accidental rate-limit abuse during development

---

## Features

- Loads a GitHub Models API token from `.env`
- Creates a LangChain chat model client targeting GitHub Models
- Defines several simple tools:
  - Calculator (restricted evaluation)
  - Current time
  - Current date
  - String reversal
  - Mock weather lookup
- Demonstrates tool-calling through a LangChain agent
- Includes explicit safety flags to control when API calls occur
- Designed to minimize token usage and avoid API spamming

---

## Project Structure

```
javascript_langchain/
├── src/
│   └── app.js
├── .gitignore
├── package.json
├── package-lock.json
└── README.md
```
---

## Requirements

- Node.js 18+
- npm (bundled with Node)
- Access to GitHub Models

Install dependencies:

npm install

---

## Environment Setup

Create a `.env` file in the project root:

GITHUB_TOKEN=your_github_models_token_here

This token is **only required when running agent tests**.
Local tool logic can be exercised without any API access if safety flags are enabled.

---

## Testing & Safety Flags (Important)

All external model calls are explicitly controlled by flags near the top of `src/app.js`.

const DRY_RUN = false;
const RUN_LOCAL_TOOL_TESTS = true;
const RUN_AGENT_TESTS = false;
const COOLDOWN_MS = 8000;
const DEBUG = false;

---

## Running the Program

From the project directory:

npm start

or

node src/app.js

---

## Rate Limiting Behavior

- HTTP 429 errors are detected
- Retries are intentionally limited
- The program fails fast with clear messaging
- Cooldowns reduce accidental API spamming
- Development defaults favor safety over speed

---

## Security Notes

- API tokens are loaded from environment variables
- `.env` files should never be committed
- The calculator tool is **not production-safe**
  - Implemented strictly for educational purposes

---

## Educational Context

This lab demonstrates:
- basic AI agent orchestration in JavaScript
- tool-based reasoning
- controlled API usage from Node.js
- safe local testing patterns

---

## License

Educational use only.
