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

FACILITY_DESCRIPTIONS: dict[str, str] = {
    "グループホーム": (
        "認知症の方が少人数で共同生活するグループホームです。"
        "家庭的な環境での認知症ケアに特化しており、生活リズムの維持と認知症状への"
        "個別対応が特に重要です。入居者間の関係性にも配慮してください。"
    ),
    "特別養護老人ホーム": (
        "重度の要介護者が入居する特別養護老人ホームです。"
        "24時間体制の介護が必要な方が多く、医療機関との連携と身体介護が重要です。"
        "褥瘡予防・拘縮予防など医療的ケアにも留意してください。"
    ),
    "介護老人保健施設": (
        "リハビリテーションを中心とした介護老人保健施設です。"
        "在宅復帰を目標とし、医療・リハビリ・介護が一体となったケアが重要です。"
        "機能維持・改善の視点を報告書に含めてください。"
    ),
    "デイサービス": (
        "日中のみ利用する通所介護（デイサービス）施設です。"
        "在宅生活を支援するサービスのため、急変時の家族連絡と医療機関への引き渡し手順が"
        "特に重要です。利用終了後の在宅環境にも配慮した対策を提案してください。"
    ),
    "自宅": (
        "在宅介護の場面です。ご家族が介護の中心となっており、"
        "訪問介護・訪問看護等の関係機関との連携と家族介護者への支援が重要です。"
        "住環境の整備や家族への指導も再発防止策に含めてください。"
    ),
}

FALL_RISK_DESCRIPTIONS: dict[str, str] = {
    "小": (
        "転倒リスク：小。見守りを基本とし、定期的な状態確認と環境整備で対応してください。"
        "自立支援を優先しながら安全を確保する方針で報告書を作成してください。"
    ),
    "中": (
        "転倒リスク：中。一部介助と積極的な見守りが必要です。"
        "移動時の付き添いと環境整備を徹底し、スタッフ間での情報共有を行ってください。"
        "リスクに応じた段階的な介助方法を具体的に記載してください。"
    ),
    "高": (
        "転倒リスク：高。常時介助・見守りが必要です。"
        "センサーマットや離床センサー等の用具活用、車椅子使用時のベルト固定を検討し、"
        "スタッフ間での申し送りを徹底してください。"
        "ヒヤリハット情報の共有と予防的介入を最優先とした対策を提案してください。"
    ),
}


def build_system_prompt(
    facility_type: str | None = None,
    fall_risk: str | None = None,
) -> str:
    """Build a system prompt tailored to the given facility type and fall risk level.

    If neither parameter is supplied the base SYSTEM_PROMPT is returned unchanged,
    preserving backward compatibility with callers that do not pass these fields.
    """
    parts = [SYSTEM_PROMPT]
    if facility_type is not None:
        parts.append(f"\n\n【施設形態】{facility_type}：{FACILITY_DESCRIPTIONS[facility_type]}")
    if fall_risk is not None:
        parts.append(f"\n\n【転倒リスクレベル】{FALL_RISK_DESCRIPTIONS[fall_risk]}")
    return "".join(parts)


_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def ask(
    messages: list[dict],
    facility_type: str | None = None,
    fall_risk: str | None = None,
) -> str:
    system = build_system_prompt(facility_type, fall_risk)
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return response.content[0].text
