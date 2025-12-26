import os
from openai import OpenAI

def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["READYMOJO_API_KEY"],
        base_url=os.environ.get("READYMOJO_BASE_URL", "https://inference.do-ai.run/v1/"),
    )

def chat_once(user_text: str) -> str:
    client = get_client()
    model = os.environ.get("READYMOJO_MODEL", "anthropic-claude-4.5-sonnet")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_text}],
        max_tokens=200,
        temperature=0.3,
    )
    return resp.choices[0].message.content
