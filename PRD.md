# BlueprintAI — Product Requirements Document (PRD)

---

# 1. Overview

## 1.1 Product Name

**BlueprintAI**

## 1.2 Elevator Pitch

BlueprintAI is an AI-powered technical diagramming assistant that transforms meeting notes, code, and ideas into professional process flows, sequence diagrams, and ERDs automatically generated in Lucidchart using Microsoft Copilot SDK and Lucid MCP.

## 1.3 Target Users

- Technical Architects
- Developers
- Business Analysts

## 1.4 Problem Statement

Technical Architects, developers, and Business Analysts spend significant time manually converting meeting notes and code into visual documentation. This process is repetitive, error-prone, and slows down project delivery.

## 1.5 Solution

BlueprintAI provides a conversational AI interface accessible through a local browser. Users can paste meeting notes, provide requirements, or point to a Salesforce codebase, and the system autonomously generates professional diagrams in Lucidchart within seconds.

---

# 2. Architecture

## 2.1 High-Level Architecture

```text
┌─────────────────────────────────────────────────────┐
│                   Browser (localhost)               │
│                   Chainlit Chat UI                  │
└─────────────────┬───────────────────────────────────┘
                  │ (websocket)
                  ▼
┌─────────────────────────────────────────────────────┐
│                     app.py                          │
│               Chainlit Entry Point                  │
│        (session management, message routing)        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                    agent.py                         │
│             Copilot SDK Agent (Brain)               │
│                                                     │
│  - System prompt                                    │
│  - Tool registration                                │
│  - Conversation memory                              │
│  - Reasoning & tool-call orchestration              │
└───────┬──────────────────────────────┬──────────────┘
        │                              │
        ▼                              ▼
┌─────────────────────┐    ┌──────────────────────────┐
│ filesystem_search   │    │        Lucid MCP         │
│       tool          │    │    (stdio connection)    │
│                     │    │                          │
│ - Filter by type    │    │ - create_document        │
│ - Keyword search    │    │ - add_shape              │
│ - Read contents     │    │ - add_line               │
│ - File metadata     │    │ - update_shape           │
└─────────────────────┘    │ - get_document           │
        │                  └──────────────────────────┘
        ▼                              │
┌─────────────────────┐               ▼
│ Local Salesforce    │    ┌──────────────────────────┐
│     Codebase        │    │    Lucidchart Cloud      │
└─────────────────────┘    └──────────────────────────┘
```

---

## 2.2 Technology Stack

| Component           | Technology                        |
| ------------------- | --------------------------------- |
| UI                  | Chainlit                          |
| Agent Orchestration | Microsoft Copilot SDK (Python)    |
| Authentication      | GitHub Personal Access Token      |
| Diagram Generation  | Lucid MCP                         |
| File Search         | Custom Python Tool                |
| Language            | Python 3.11+                      |
| Environment         | Python virtual environment (venv) |
| Config Management   | python-dotenv + `.env`            |

---

# 3. Project Structure

```text
/blueprint-ai
├── app.py
├── agent.py
├── tools/
│   ├── __init__.py
│   ├── filesystem_search.py
│   └── lucid_mcp.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── chainlit.md
└── README.md
```

---

# 4. Functional Requirements

## 4.1 Chat Interface (Chainlit)

| ID    | Requirement         | Details                                               |
| ----- | ------------------- | ----------------------------------------------------- |
| UI-01 | Chat window         | Single chat window with persistent message history    |
| UI-02 | Send button         | User can submit via button or Enter key               |
| UI-03 | Message display     | Clear distinction between user and assistant messages |
| UI-04 | Link rendering      | URLs render as clickable links                        |
| UI-05 | Session persistence | Conversation retained for browser session             |
| UI-06 | Welcome message     | Display onboarding message on load                    |
| UI-07 | Streaming responses | Responses stream token-by-token                       |

---

## 4.2 Agent (Copilot SDK)

| ID    | Requirement             | Details                                                    |
| ----- | ----------------------- | ---------------------------------------------------------- |
| AG-01 | System prompt           | Agent follows BlueprintAI system prompt                    |
| AG-02 | Tool access             | Agent can access filesystem_search and Lucid MCP tools     |
| AG-03 | Autonomous tool calling | Agent determines tool usage automatically                  |
| AG-04 | Full session memory     | Conversation context retained for current session          |
| AG-05 | Generate-first behavior | Agent generates diagrams immediately without clarification |
| AG-06 | Iteration support       | Existing Lucidchart documents updated in-place             |
| AG-07 | Document ID tracking    | Lucid document IDs stored in memory                        |
| AG-08 | Graceful degradation    | Mermaid fallback if Lucid MCP fails                        |
| AG-09 | Error communication     | Clear user-facing error messaging                          |
| AG-10 | Diagram type detection  | Automatically infer process flow, sequence diagram, or ERD |

---

## 4.3 Filesystem Search Tool

| ID    | Requirement         | Details                                 |
| ----- | ------------------- | --------------------------------------- |
| FS-01 | Default folder path | Loaded from `SALESFORCE_CODEBASE_PATH`  |
| FS-02 | Folder override     | User can override path during session   |
| FS-03 | File filtering      | Supports Salesforce metadata extensions |
| FS-04 | Recursive traversal | Searches nested directories             |
| FS-05 | Keyword search      | Searches filenames and file contents    |
| FS-06 | Return contents     | Returns relevant file content           |
| FS-07 | Result limiting     | Maximum 10 results                      |
| FS-08 | Metadata return     | Include filename, path, and file type   |

### Supported File Types

```text
.cls
.trigger
.flow-meta.xml
.object-meta.xml
.field-meta.xml
```

---

## 4.4 Lucid MCP Integration

| ID    | Requirement        | Details                             |
| ----- | ------------------ | ----------------------------------- |
| LC-01 | stdio connection   | Connect via subprocess              |
| LC-02 | Authentication     | Pre-authenticated MCP configuration |
| LC-03 | Document creation  | Create Lucidchart documents         |
| LC-04 | Shape creation     | Add nodes/shapes                    |
| LC-05 | Connector creation | Add lines/connectors                |
| LC-06 | Document update    | Modify existing diagrams            |
| LC-07 | Document retrieval | Read current document state         |
| LC-08 | Link return        | Return clickable Lucidchart URL     |
| LC-09 | Error handling     | Trigger Mermaid fallback on failure |

---

# 5. Non-Functional Requirements

| ID    | Requirement      | Details                            |
| ----- | ---------------- | ---------------------------------- |
| NF-01 | Local execution  | Entire app runs locally            |
| NF-02 | Startup time     | Ready within 10 seconds            |
| NF-03 | Response latency | Streaming begins within 3 seconds  |
| NF-04 | No database      | In-memory session state only       |
| NF-05 | Single user      | Supports one concurrent local user |
| NF-06 | Cross-platform   | macOS and Windows compatible       |

---

# 6. System Prompt

```text
You are BlueprintAI, a technical diagramming assistant built for Technical Architects, Developers, and Business Analysts.

Your capabilities:
- Generate process flow diagrams from meeting notes or code
- Generate sequence diagrams from meeting notes or code
- Generate entity-relationship diagrams (ERDs) from meeting notes or code
- Search a local Salesforce codebase to understand system structure

Your behavior:
- When a user provides meeting notes, code, or ideas, immediately generate your best attempt at the appropriate diagram type. Do NOT ask clarifying questions before generating.
- Infer the correct diagram type (process flow, sequence diagram, or ERD) from context. If truly ambiguous, default to a process flow diagram.
- Use the filesystem_search tool to find relevant Salesforce code when needed.
- Use Lucid MCP tools to create diagrams directly in Lucidchart.
- After creating a diagram, return the Lucidchart document link to the user.
- When the user requests changes to an existing diagram, update the same document rather than creating a new one.
- If Lucidchart tools fail, render the diagram as Mermaid syntax in the chat as a fallback.
- If you cannot find relevant files in the codebase, inform the user and ask for clarification.

Your tone:
- Concise, professional, and action-oriented.
- No unnecessary preamble. Get to the output fast.

Tools available:
- filesystem_search
- Lucid MCP tools
```

---

# 7. Configuration

## 7.1 `.env` File

```env
# GitHub PAT for Copilot SDK authentication
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Default Salesforce codebase path
SALESFORCE_CODEBASE_PATH=/path/to/salesforce/project

# Lucid MCP server command
LUCID_MCP_COMMAND=npx
LUCID_MCP_ARGS=@lucid/mcp-server
```

---

## 7.2 `config.py` Responsibilities

- Load environment variables from `.env`
- Expose typed configuration values
- Provide default values where appropriate
- Validate required variables at startup
- Fail fast if `GITHUB_TOKEN` is missing

---

# 8. User Flows

## 8.1 Meeting Notes → Process Flow Diagram

```text
1. User opens localhost:8000
2. Chainlit displays welcome message
3. User pastes meeting notes
4. Agent receives input
5. Agent infers process flow diagram
6. Agent creates Lucidchart document
7. Agent parses notes into workflow steps
8. Agent adds shapes and connectors
9. Agent receives Lucidchart URL
10. Agent returns clickable link
```

---

## 8.2 Salesforce Codebase → ERD

```text
1. User requests ERD generation
2. Agent searches Salesforce metadata
3. Agent reads objects and relationships
4. Agent creates Lucidchart document
5. Agent adds entity nodes
6. Agent creates relationship connectors
7. Agent returns Lucidchart link
```

---

## 8.3 Iteration Flow

```text
1. User requests modification
2. Agent retrieves stored document ID
3. Agent reads current document
4. Agent updates shapes/connectors
5. Agent returns updated document link
```

---

## 8.4 Fallback Flow

```text
1. User submits notes
2. Lucid MCP fails
3. Agent catches exception
4. Agent generates Mermaid diagram
5. Agent returns Mermaid syntax in chat
```

---

## 8.5 Folder Override Flow

```text
1. User specifies alternate codebase path
2. Agent stores override in session
3. Agent confirms path update
4. Future searches use override path
```

---

# 9. Tool Specifications

## 9.1 `filesystem_search`

### Function Signature

```python
filesystem_search(
    query: str,
    folder_path: str | None = None
) -> list[FileResult]
```

### Parameters

| Parameter   | Type | Required | Description                   |
| ----------- | ---- | -------- | ----------------------------- |
| query       | str  | Yes      | Natural language search query |
| folder_path | str  | No       | Optional override path        |

### Return Type

```python
FileResult:
  - file_name: str
  - relative_path: str
  - file_type: str
  - content: str
```

### Internal Logic

1. Resolve folder path
2. Recursively traverse directories
3. Filter supported Salesforce metadata files
4. Extract query keywords
5. Score files based on relevance
6. Return top 10 results
7. Truncate content to 2000 chars/file

---

## 9.2 Lucid MCP Tools

| Tool            | Purpose                     | Key Parameters                                |
| --------------- | --------------------------- | --------------------------------------------- |
| create_document | Create Lucidchart document  | title                                         |
| add_shape       | Add diagram node            | document_id, shape_type, text, position       |
| add_line        | Add connector               | document_id, source_shape_id, target_shape_id |
| update_shape    | Modify existing shape       | document_id, shape_id                         |
| get_document    | Retrieve document structure | document_id                                   |

---

# 10. Dependencies

## 10.1 Python Dependencies

```txt
chainlit>=1.0.0
copilot-sdk>=0.1.0
mcp>=1.0.0
python-dotenv>=1.0.0
```

---

## 10.2 External Dependencies

| Dependency          | Purpose                  |
| ------------------- | ------------------------ |
| Node.js v18+        | Required for Lucid MCP   |
| `@lucid/mcp-server` | Lucid MCP server package |

---

# 11. Startup & Run Instructions

## 11.1 First-Time Setup

```bash
# Clone repository
git clone <repo-url>
cd blueprint-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Verify Node.js
node --version
```

---

## 11.2 Running the Application

```bash
chainlit run app.py -w
```

Application URL:

```text
http://localhost:8000
```

---

# 12. Welcome Message (`chainlit.md`)

```markdown
# 🏗️ BlueprintAI

Welcome! I'm BlueprintAI — your AI diagramming assistant.

## What I can do

- Turn meeting notes into process flow diagrams
- Generate sequence diagrams from code or descriptions
- Create ERDs from your Salesforce object model

## How to use me

- Paste meeting notes and I’ll generate a diagram
- Ask me to analyze your Salesforce codebase
- Request updates to an existing diagram

Let’s get started — paste your notes or tell me what you need!
```

---

# 13. Acceptance Criteria

## 13.1 MVP (Hackathon Demo)

| #   | Criteria                                       | Status |
| --- | ---------------------------------------------- | ------ |
| 1   | User can access Chainlit UI                    | ⬜     |
| 2   | User receives streamed responses               | ⬜     |
| 3   | Meeting notes generate Lucidchart process flow | ⬜     |
| 4   | Agent returns clickable Lucidchart link        | ⬜     |
| 5   | User can update existing diagrams              | ⬜     |
| 6   | Mermaid fallback works on failure              | ⬜     |
| 7   | Session memory retained                        | ⬜     |

---

## 13.2 Stretch Goals

| #   | Criteria                     | Status |
| --- | ---------------------------- | ------ |
| 8   | Salesforce codebase analysis | ⬜     |
| 9   | ERD generation from metadata | ⬜     |
| 10  | Sequence diagrams from Apex  | ⬜     |
| 11  | Folder path override support | ⬜     |

---

# 14. Risks & Mitigations

| Risk                         | Impact                    | Mitigation                            |
| ---------------------------- | ------------------------- | ------------------------------------- |
| Lucid MCP API mismatch       | Diagram creation failure  | Inspect MCP tool registry dynamically |
| Copilot SDK integration gaps | Tool orchestration issues | Build MCP wrapper layer               |
| Large Salesforce codebase    | Token/context overflow    | Limit files and truncate content      |
| Streaming incompatibility    | Poor UX                   | Fallback to non-streaming responses   |
| Invalid GitHub PAT           | Authentication failure    | Validate credentials at startup       |

---

# 15. Future Enhancements

- File upload support
- Audio/video transcription
- Multi-user authentication
- Diagram templates
- Export to PNG/PDF/Mermaid
- Jira and Confluence integration
- Additional Salesforce metadata support

# 16. Resources

- Copilot SDK for Python - https://github.com/github/copilot-sdk/tree/main/python
- Lucid MCP - https://help.lucid.co/hc/en-us/articles/42578801807508-Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server?_gl=1%2A190jo7f%2A_gcl_au%2AMTEyNTg1NTcxMy4xNzc5NDA1Njkz&anonId=0.5d08afe719e4cd81ccf&sessionDate=2026-05-25T19%3A10%3A21.952Z&sessionId=0.90cc89819e608b4e84
  es
