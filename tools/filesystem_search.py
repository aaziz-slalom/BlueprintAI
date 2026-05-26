"""
tools/filesystem_search.py

Searches a local Salesforce codebase for relevant files based on a query.
Returns up to 10 matches with filename, path, file type, and truncated content.
"""

import json
import os
from pathlib import Path
from typing import Any

import config

SUPPORTED_EXTENSIONS = {
    ".cls",
    ".trigger",
    ".flow-meta.xml",
    ".object-meta.xml",
    ".field-meta.xml",
}
MAX_RESULTS = 10
MAX_CONTENT_CHARS = 2000


def _search(query: str, folder_path: str | None = None) -> list[dict[str, str]]:
    base = folder_path or config.SALESFORCE_CODEBASE_PATH
    if not base or not os.path.isdir(base):
        return [{"error": f"Folder not found or not set: '{base}'. Use the folder_path parameter or set SALESFORCE_CODEBASE_PATH in .env."}]

    keywords = [kw.lower() for kw in query.split() if len(kw) > 2]
    scored: list[tuple[int, dict[str, str]]] = []

    for root, _, files in os.walk(base):
        for filename in files:
            if not any(filename.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                continue
            filepath = os.path.join(root, filename)
            try:
                content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            score = sum(
                1 for kw in keywords if kw in filename.lower() or kw in content.lower()
            )
            if score > 0:
                scored.append((
                    score,
                    {
                        "file_name": filename,
                        "relative_path": os.path.relpath(filepath, base),
                        "file_type": "".join(Path(filename).suffixes),
                        "content": content[:MAX_CONTENT_CHARS],
                    },
                ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:MAX_RESULTS]]


def make_tool() -> dict[str, Any]:
    """Return a copilot SDK Tool dict for filesystem_search."""
    from copilot.tools import Tool, ToolInvocation, ToolResult

    async def handler(invocation: ToolInvocation) -> ToolResult:
        args = invocation.arguments or {}
        if isinstance(args, str):
            import json as _json
            args = _json.loads(args)
        results = _search(
            query=args.get("query", ""),
            folder_path=args.get("folder_path"),
        )
        return ToolResult(
            text_result_for_llm=json.dumps(results, indent=2),
            result_type="success",
        )

    return Tool(
        name="filesystem_search",
        description=(
            "Search the local Salesforce codebase for relevant files. "
            "Searches filenames and file contents. "
            "Supported types: .cls, .trigger, .flow-meta.xml, .object-meta.xml, .field-meta.xml."
        ),
        handler=handler,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query (e.g. 'Account trigger opportunity').",
                },
                "folder_path": {
                    "type": "string",
                    "description": "Optional override for the Salesforce codebase folder path.",
                },
            },
            "required": ["query"],
        },
    )
