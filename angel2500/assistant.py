"""OpenAI text-only assistant; no tool execution or exchange permissions."""
import os


def answer_question(message: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=20.0, max_retries=1)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": (
                    "You are Angel2500 AI Core v5, an informational assistant. "
                    "You cannot place trades, transfer funds, run commands or access accounts. "
                    "Never claim that you performed external actions."
                )},
                {"role": "user", "content": message},
            ],
            max_tokens=700,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise RuntimeError("Assistant API call failed") from exc
