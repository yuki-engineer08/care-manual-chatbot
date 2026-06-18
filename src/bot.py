import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """あなたは事故発見者の介護士です。
事故発見時と後の様子を以下の情報を基に、優れた出力してください。
また、それぞれご利用者様要因、介護側要因、環境要因、再発防止のための対策を100字以内書いてください。
再発防止案は可能な範囲内で対象に寄り添った対策（生活リズムなど）で出力してください。
それぞれまとめて文章化してください。"""

_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def ask(messages: list[dict]) -> str:
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text
