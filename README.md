# BlueprintAI — Genie

> AI-powered diagramming assistant. Paste meeting notes or code and Genie generates professional diagrams in Lucidchart automatically.

---

## Prerequisites

| Requirement    | Version             | Notes                                    |
| -------------- | ------------------- | ---------------------------------------- |
| Python         | 3.11+               | A `.venv` is already present in the repo |
| Node.js        | 18+                 | Required by `mcp-remote` for Lucid MCP   |
| GitHub Copilot | Active subscription | PAT used for Copilot SDK auth            |
| Lucid account  | Free or paid        | OAuth login on first run                 |

---

## First-Time Setup

### 1. Activate the virtual environment

```bash
cd BlueprintAI
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# Required — GitHub Personal Access Token with Copilot access
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — path to a local Salesforce codebase for ERD/code analysis
SALESFORCE_CODEBASE_PATH=/path/to/your/salesforce/project

# Optional — model override (default: claude-sonnet-4-5)
MODEL=claude-sonnet-4-5
```

To generate a GitHub PAT:  
**GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**  
Scopes needed: `read:user` (Copilot uses your account's Copilot subscription).

---

## Running the App

```bash
source .venv/bin/activate   # if not already active
chainlit run app.py -w --port 8001
```

Then open **http://localhost:8001** in your browser.

The `-w` flag enables hot-reload — the server restarts automatically when you edit source files.

---

## First Run — Lucid Authentication

On first use, the Lucid MCP connection (`mcp-remote`) will open a **browser tab** asking you to sign in to Lucid and authorize the integration. This happens once. After that, credentials are cached and subsequent runs connect silently.

If the browser tab doesn't open automatically, check the terminal — `mcp-remote` prints the auth URL.

---

## Project Structure

```
BlueprintAI/
├── app.py                    # Chainlit UI and message routing
├── agent.py                  # Copilot SDK session (Genie brain)
├── config.py                 # Environment config loader
├── tools/
│   ├── __init__.py
│   └── filesystem_search.py  # Salesforce codebase search tool
├── requirements.txt
├── .env.example              # Copy to .env and fill in values
├── chainlit.md               # Chat welcome message
├── LUCID_MCP_FINDINGS.md     # Lucid MCP research & tool reference
└── README.md                 # This file
```

---

## What Genie Can Do

| Input                             | Output                                |
| --------------------------------- | ------------------------------------- |
| Meeting notes                     | Process flow diagram in Lucidchart    |
| Code or architecture description  | Sequence diagram in Lucidchart        |
| Salesforce metadata path          | ERD in Lucidchart                     |
| Modification request              | Updates the existing diagram in place |
| Any of the above (if Lucid fails) | Mermaid diagram rendered in chat      |

---

## Troubleshooting

**`GITHUB_TOKEN is required` error on startup**  
→ Make sure you have a `.env` file (not just `.env.example`) with `GITHUB_TOKEN` set.

**Lucid auth browser tab doesn't appear**  
→ Run `npx -y mcp-remote https://mcp.lucid.app/mcp` in a separate terminal to trigger the auth flow manually, then restart the app.

**`chainlit: command not found`**  
→ Your venv is not active. Run `source .venv/bin/activate` first.

**Agent responds but no diagram is created**  
→ The Lucid MCP may not have authenticated yet. Check the terminal for an auth URL from `mcp-remote`.

**Salesforce search returns no results**  
→ Confirm `SALESFORCE_CODEBASE_PATH` in `.env` points to a valid directory containing `.cls`, `.trigger`, or metadata XML files.
