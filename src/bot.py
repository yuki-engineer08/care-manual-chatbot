import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """あなたは介護施設で働くスタッフを支援する専門アシスタントです。
介護現場におけるベストプラクティス(利用者の安全確保、感染対策、認知症ケア、
記録の取り方、多職種連携、ハラスメント・事故防止など)に基づいて、
具体的で実践的なアドバイスを日本語で分かりやすく回答してください。
医療的な診断や処方が必要な内容については、必ず医師・看護師等の専門職への
相談を促してください。"""

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
