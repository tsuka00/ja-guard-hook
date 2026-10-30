"""main.py を Claude Code と同じくサブプロセスとして起動し、標準入出力と終了コードを検証する。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ENTRY_POINT = Path(__file__).resolve().parent.parent / "main.py"


def run_hook(
    payload: dict[str, object], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(ENTRY_POINT)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        env={**os.environ, **(env or {})},
        check=False,
    )


def stop_payload(message: str) -> dict[str, object]:
    return {"hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": message}


def test_english_response_writes_additional_context() -> None:
    result = run_hook(
        stop_payload("I have finished the refactoring and all tests are passing now.")
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"] == "Stop"


def test_japanese_response_writes_nothing() -> None:
    result = run_hook(stop_payload("リファクタリングが終わり、テストもすべて通りました。"))

    assert result.returncode == 0
    assert result.stdout == b""


def test_input_is_read_as_utf8_regardless_of_locale() -> None:
    # 標準入出力の既定の文字コードが ASCII の環境でも、日本語を含む入力で落ちない
    result = run_hook(
        stop_payload("I have finished the refactoring and updated the docs. 日本語も少し。"),
        env={"PYTHONIOENCODING": "ascii"},
    )

    assert result.returncode == 0
    assert result.stderr == b""
    assert json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"] == "Stop"
