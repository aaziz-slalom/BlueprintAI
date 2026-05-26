"""
app.py

Chainlit entry point for BlueprintAI — powered by Genie.
Each browser session gets its own Copilot SDK agent and session.
"""

from __future__ import annotations

import chainlit as cl
from chainlit.input_widget import Select
from copilot import CopilotClient
from copilot.client import SubprocessConfig

from agent import BlueprintAgent
import config

MODEL_SETTING_ID = "model"


def _session_env() -> dict:
    env = cl.user_session.get("env")
    return env if isinstance(env, dict) else {}


def _resolved_token() -> str:
    return config.resolve_github_token(_session_env())


async def _fetch_models(github_token: str) -> list[str]:
    """Fetch model IDs from Copilot SDK, keeping a stable fallback list on failure."""
    if not github_token:
        return [config.MODEL]

    client = CopilotClient(SubprocessConfig(github_token=github_token))
    try:
        await client.start()
        models = await client.list_models()
        model_ids = sorted({m.id for m in models if getattr(m, "id", "")})
        return model_ids or [config.MODEL]
    finally:
        try:
            await client.stop()
        except Exception:
            pass


async def _send_model_picker(token: str) -> str:
    try:
        models = await _fetch_models(token)
    except Exception:
        models = [config.MODEL]

    current_model = cl.user_session.get("selected_model") or config.MODEL
    if current_model not in models:
        current_model = models[0]

    settings = await cl.ChatSettings(
        [
            Select(
                id=MODEL_SETTING_ID,
                label="Genie Model",
                values=models,
                initial_value=current_model,
            )
        ]
    ).send()

    selected_model = str(settings.get(MODEL_SETTING_ID) or current_model)
    cl.user_session.set("selected_model", selected_model)
    cl.user_session.set("available_models", models)
    return selected_model


async def _restart_agent_if_needed(force: bool = False):
    token = _resolved_token()
    model = str(cl.user_session.get("selected_model") or config.MODEL)

    current_token = str(cl.user_session.get("active_github_token") or "")
    current_model = str(cl.user_session.get("active_model") or "")
    current_agent: BlueprintAgent | None = cl.user_session.get("agent")

    if not token:
        if current_agent:
            await current_agent.stop()
            cl.user_session.set("agent", None)
        await cl.Message(
            content=(
                "⚠️ Genie needs a GitHub token. Add `GITHUB_TOKEN` in `.env` or use the sidebar env input, "
                "then refresh or send another message."
            )
        ).send()
        return

    if not force and current_agent and token == current_token and model == current_model:
        return

    if current_agent:
        await current_agent.stop()

    next_agent = BlueprintAgent(github_token=token, model=model)
    await next_agent.start()
    cl.user_session.set("agent", next_agent)
    cl.user_session.set("active_github_token", token)
    cl.user_session.set("active_model", model)


@cl.on_chat_start
async def on_chat_start():
    token = _resolved_token()
    selected_model = await _send_model_picker(token)
    cl.user_session.set("selected_model", selected_model)

    try:
        await _restart_agent_if_needed(force=True)
    except Exception as e:
        await cl.Message(
            content=f"⚠️ Failed to start Genie: {e}\n\nCheck `.env` or the sidebar token input."
        ).send()


@cl.on_settings_update
async def on_settings_update(settings):
    selected_model = str(settings.get(MODEL_SETTING_ID) or config.MODEL)
    cl.user_session.set("selected_model", selected_model)
    try:
        await _restart_agent_if_needed(force=False)
    except Exception as e:
        await cl.Message(content=f"⚠️ Could not apply settings: {e}").send()


@cl.on_message
async def on_message(message: cl.Message):
    agent: BlueprintAgent | None = cl.user_session.get("agent")
    if agent is None:
        try:
            await _restart_agent_if_needed(force=False)
            agent = cl.user_session.get("agent")
        except Exception as e:
            await cl.Message(content=f"Genie is not initialized yet: {e}").send()
            return

    if agent is None:
        await cl.Message(content="Genie is not initialized yet. Add token in sidebar or `.env`, then retry.").send()
        return

    thinking_msg = cl.Message(content="*Thinking…*")
    await thinking_msg.send()

    try:
        full_response = await agent.send_message(message.content)
        thinking_msg.content = full_response
    except Exception as e:
        thinking_msg.content = f"⚠️ Error: {e}"

    await thinking_msg.update()


@cl.on_chat_end
async def on_chat_end():
    agent: BlueprintAgent | None = cl.user_session.get("agent")
    if agent:
        await agent.stop()
