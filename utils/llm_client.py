"""
LLM Client - Handles all LLM interactions with Bring-Your-Own-Key support.
Works with any OpenAI-compatible API endpoint.
"""
import os
import json
from pathlib import Path
from openai import OpenAI

# Base directory for loading system prompts
BASE_DIR = Path(__file__).parent.parent
SYSTEM_PROMPTS_DIR = BASE_DIR / "system_prompts"


def get_system_prompt(name: str) -> str:
    """Load a system prompt file by name."""
    prompt_path = SYSTEM_PROMPTS_DIR / f"{name}.txt"
    if prompt_path.exists():
        return prompt_path.read_text().strip()
    return ""


def build_system_prompt(mode: str = "base", context: str = "") -> str:
    """
    Build a complete system prompt by combining base + mode-specific prompts.

    Args:
        mode: One of "base", "tutor_mode", "ask_mode"
        context: Additional context (e.g., syllabus summary) to inject
    """
    base = get_system_prompt("base")
    mode_prompt = get_system_prompt(mode) if mode != "base" else ""

    system_prompt = base
    if mode_prompt:
        system_prompt += "\n\n" + mode_prompt
    if context:
        system_prompt += f"\n\n## COURSE CONTEXT\n{context}"

    return system_prompt


def get_client(api_key: str = None, base_url: str = None, model: str = None):
    """Create an OpenAI client with the provided or default credentials."""
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    if not base_url:
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not model:
        model = os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("No API key provided. Enter your key in the sidebar or set OPENAI_API_KEY env variable.")

    return OpenAI(api_key=api_key, base_url=base_url), model


def chat_completion(
    user_message: str,
    system_prompt: str = None,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
    mode: str = "base",
    context: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """
    Send a chat completion request to the LLM.

    Returns the assistant's text response.
    """
    client, model_name = get_client(api_key, base_url, model)

    if system_prompt:
        full_system = system_prompt
    else:
        full_system = build_system_prompt(mode, context)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content


def chat_completion_stream(
    user_message: str,
    system_prompt: str = None,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
    mode: str = "base",
    context: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
):
    """Stream a chat completion response (for real-time UI)."""
    client, model_name = get_client(api_key, base_url, model)

    if system_prompt:
        full_system = system_prompt
    else:
        full_system = build_system_prompt(mode, context)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def structured_output(
    user_message: str,
    system_prompt: str = None,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
    prompt_name: str = None,
    temperature: float = 0.3,
) -> dict:
    """
    Get a structured JSON response from the LLM.
    Uses a specific system prompt for structured output tasks.
    """
    if system_prompt:
        full_system = system_prompt
    elif prompt_name:
        full_system = get_system_prompt(prompt_name)
        if not full_system:
            raise ValueError(f"System prompt '{prompt_name}' not found.")
    else:
        raise ValueError("Provide either system_prompt or prompt_name.")

    client, model_name = get_client(api_key, base_url, model)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from markdown code blocks
        content = content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if "\n" in content:
                content = content.split("\n", 1)[1]
            return json.loads(content.strip())
        raise
