"""Stop hook の入出力。

最終応答（last_assistant_message）が英語主体なら、additionalContext で日本語での書き直しを求める。
decision: block ではなく additionalContext を使うのは、意図どおりの差し戻しを hook error と
表示させないため（docs/decisions/0004）。
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping

from ja_guard.config import load_thresholds
from ja_guard.detector import is_english_dominant

REWRITE_INSTRUCTION = (
    "直前の応答が英語で書かれていました。ユーザーは日本語での応答を求めています。"
    "日本語で書き直してください。"
    "コード・コマンド・識別子・固有名詞は原文のままで構いません。"
    "書き直しであることの説明や謝罪は書かず、以降の応答もすべて日本語で書いてください。"
)


def handle(raw_input: str, environ: Mapping[str, str]) -> str | None:
    """hook の入力（JSON 文字列）を受け取り、差し戻すときだけ出力（JSON 文字列）を返す。"""
    try:
        payload = json.loads(raw_input)
    except ValueError:
        return None
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "Stop":
        return None
    # 書き直しの後のターンでは差し戻さない。書き直しも英語だったときに繰り返さないため
    if payload.get("stop_hook_active") is True:
        return None

    response = payload.get("last_assistant_message")
    if not isinstance(response, str):
        return None
    if not is_english_dominant(response, load_thresholds(environ)):
        return None

    return json.dumps(
        {"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": REWRITE_INSTRUCTION}},
        ensure_ascii=False,
    )


def main() -> int:
    # ロケールの文字コードに依存せず、UTF-8 で読み書きする
    raw_input = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    output = handle(raw_input, os.environ)
    if output is not None:
        sys.stdout.buffer.write(output.encode("utf-8"))
    return 0
