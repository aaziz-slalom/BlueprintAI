"""
agent.py

Wraps the GitHub Copilot SDK session for BlueprintAI.
Exposes a simple send_message() that streams tokens to a callback.
"""

import asyncio
from typing import Any, Awaitable, Callable, Optional

from copilot.client import SubprocessConfig
import config
from tools.filesystem_search import make_tool

SYSTEM_PROMPT = """You are Genie, the AI diagramming assistant made by BlueprintAI, built for Technical Architects, Developers, and Business Analysts.

Your capabilities:
- Generate process flow diagrams from meeting notes or code
- Generate sequence diagrams from meeting notes or code
- Generate entity-relationship diagrams (ERDs) from meeting notes or code
- Search a local Salesforce codebase to understand system structure

Your behavior:
- When a user provides meeting notes, code, or ideas, immediately generate your best attempt at the appropriate diagram type. Do NOT ask clarifying questions before generating.
- Infer the correct diagram type (process flow, sequence diagram, or ERD) from context. If truly ambiguous, default to a process flow diagram.
- Use the filesystem_search tool to find relevant Salesforce code when needed.
- Use the Lucid MCP tools to create diagrams directly in Lucidchart.
- After creating a diagram, return the Lucidchart document link to the user.
- When the user requests changes to an existing diagram, update the same document rather than creating a new one.
- If Lucidchart tools fail or are unavailable, render the diagram as Mermaid syntax in the chat as a fallback.
- If you cannot find relevant files in the codebase, inform the user and ask for clarification.

Your tone:
- Concise, professional, and action-oriented.
- No unnecessary preamble. Get to the output fast."""


def _approve_all(request, invocation):
    return {"kind": "approved"}


class BlueprintAgent:
    def __init__(self, github_token: str, model: str):
        self.github_token = github_token.strip()
        self.model = model.strip() or config.MODEL
        self._client = None
        self._session = None

    async def start(self):
        from copilot import CopilotClient

        if not self.github_token:
            raise ValueError("Missing GitHub token. Set GITHUB_TOKEN in .env or provide it in the app sidebar.")

        self._client = CopilotClient(SubprocessConfig(github_token=self.github_token))
        await self._client.start()

        fs_tool = make_tool()

        self._session = await self._client.create_session(
            model=self.model,
            streaming=True,
            system_message={
                "mode": "replace",
                "content": SYSTEM_PROMPT,
            },
            tools=[fs_tool],
            on_permission_request=_approve_all,
            mcp_servers={
                "lucid": {
                    "type": "local",
                    "command": config.LUCID_MCP_COMMAND,
                    "args": config.LUCID_MCP_ARGS,
                    "tools": ["*"],
                }
            },
        )

    async def send_message(
        self,
        message: str,
        on_token: Optional[Callable[[str], Awaitable[None]]] = None,
    ) -> str:
        """Send a message and stream tokens via on_token callback. Returns full response."""
        if not self._session:
            raise RuntimeError("Agent not started. Call start() first.")

        queue: asyncio.Queue = asyncio.Queue()

        def _event_handler(event):
            queue.put_nowait(event)

        unsubscribe = self._session.on(_event_handler)
        await self._session.send(message)

        full_response: list[str] = []
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=180.0)
                event_type = _event_type(event)

                if event_type == "session.idle":
                    break

                if event_type == "assistant.message_delta":
                    delta = _extract_text(event)
                    if delta:
                        full_response.append(delta)
                        if on_token:
                            await on_token(delta)

                elif event_type == "assistant.message":
                    # Non-streaming fallback: full content in one event
                    content = _extract_text(event)
                    if content and not full_response:
                        full_response.append(content)
                        if on_token:
                            await on_token(content)
        except asyncio.TimeoutError:
            full_response.append("\n\n[Response timed out]")
        finally:
            unsubscribe()

        return "".join(full_response)

    async def stop(self):
        if self._session:
            try:
                await self._session.disconnect()
            except Exception:
                pass
        if self._client:
            try:
                await self._client.stop()
            except Exception:
                pass


def _event_type(event: Any) -> str:
    if isinstance(event, dict):
        return str(event.get("type", ""))
    return str(getattr(event, "type", ""))


def _event_data(event: Any) -> Any:
    if isinstance(event, dict):
        return event.get("data", {})
    return getattr(event, "data", {})


def _extract_text(event: Any) -> str:
    data = _event_data(event)

    if isinstance(data, dict):
        return str(data.get("delta_content") or data.get("deltaContent") or data.get("content") or "")

    return str(
        getattr(data, "delta_content", None)
        or getattr(data, "deltaContent", None)
        or getattr(data, "content", None)
        or ""
    )
