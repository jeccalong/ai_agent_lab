<p align="center">
  <img src="assets/header.png" alt="AI Agent Lab – Python and JavaScript" />
</p>

<div align="center" style="display:flex; flex-wrap:wrap; justify-content:center; gap:8px;">

<p align="center">
  <!-- Top of page / intro -->
  <a href="#">
    <img src="assets/overview.png" width="130" alt="Project Overview">
  </a>

  <a href="#repository-structure">
    <img src="assets/structure.png" width="130" alt="Repository Structure">
  </a>

  <a href="#python-implementation-primary">
    <img src="assets/python.png" width="130" alt="Python Implementation">
  </a>

  <a href="#javascript-implementation">
    <img src="assets/javascript.png" width="130" alt="JavaScript Implementation">
  </a>

  <a href="#environment-variables">
    <img src="assets/variables.png" width="130" alt="Environment Variables">
  </a>

  <a href="#api-limits">
    <img src="assets/api_limits.png" width="130" alt="API Limits and Safety">
  </a>

  <a href="#educational-intent">
    <img src="assets/intent.png" width="130" alt="Educational Intent">
  </a>

  <a href="#license">
    <img src="assets/license.png" width="130" alt="License">
  </a>
</p>
</div>





# AI Agent Lab

This repository contains a **student lab project** exploring how to build a simple, tool‑calling AI agent using **LangChain** and **GitHub Models**, implemented in **both Python and JavaScript**.

The emphasis of this project is **agent orchestration**, not prompt engineering.  
It demonstrates how an agent:
- receives user input
- reasons about whether tools are required
- invokes local tools safely
- incorporates tool output into a final response
- operates within explicit rate‑limit and cost‑control boundaries

This work was completed as part of the [Code:You](https://code-you.org/) AI curriculum.
<p align="center">
  <img alt="AI Agents" src="https://img.shields.io/badge/AI%20Agents-Orchestration-8C2053" />
  <img alt="LangChain" src="https://img.shields.io/badge/LangChain-Framework-8C2053" />
  <img alt="GitHub Models" src="https://img.shields.io/badge/GitHub%20Models-LLM%20API-8C2053?logo=github&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-8C2053?logo=python&logoColor=white" />
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-ES2022+-8C2053?logo=javascript&logoColor=white" />
</p>

---

## Repository Structure

```
ai_agent_lab/
├── python_langchain/        # Python implementation (primary reference)
├── javascript_langchain/    # JavaScript (Node.js) implementation
├── assets/                  # Images
├── example.env              # Sample .env
└── README.md                # You are here
```

---

## Python Implementation (Primary)

**Location:** `python_langchain/`

The Python implementation is the **canonical reference** for this lab and contains the most complete demonstration of agent behavior.

Key features include:
- LangChain agent construction using `create_agent`
- Tool definitions for calculator, time, string reversal, and mock weather
- Explicit retry handling for API rate limits
- Structured logging for agent execution
- Safe environment variable loading via `.env`
- Clear separation between configuration, tools, agent construction, and execution

The Python folder includes its **own README** with detailed setup and execution instructions.  
This main README intentionally avoids duplicating those details.

➡️ See `python_langchain/README.md` for full Python documentation.

---

## JavaScript Implementation

**Location:** `javascript_langchain/`

The JavaScript implementation mirrors the Python agent conceptually while adapting to:
- Node.js execution patterns
- async/await orchestration
- JavaScript‑specific LangChain APIs

It exists primarily to highlight **language‑level differences** rather than introduce new agent behavior.

➡️ See `javascript_langchain/README.md` for details.

---

## Environment Variables

Both implementations require a GitHub Models API token.

Create a `.env` file based on `example.env`:

```
GITHUB_TOKEN=your_token_here
```

Notes:
- Tokens are never committed to version control
- The same token can be reused across Python and JavaScript
- API calls are guarded by runtime logic to prevent accidental usage

---

## API Limits

A core design goal of this lab is **defensive API usage**.

Safety mechanisms demonstrated include:
- minimal request payloads
- explicit retry limits
- cooldown delays between retries
- early failure on missing credentials
- optional rate‑limit probing before execution

The guiding principle is:
**local logic first, API calls last.**

---

## Educational Intent

This project is designed to:
- build intuition for how agents differ from chat completions
- demonstrate practical tool orchestration
- compare Python and JavaScript agent implementations
- model responsible LLM usage patterns

It is **not production software** and intentionally favors clarity over abstraction.

---

## License

Educational use only.
