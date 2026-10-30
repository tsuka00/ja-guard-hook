"""main.py を Claude Code と同じくサブプロセスとして起動し、標準入出力と終了コードを検証する。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ENTRY_POINT = Path(__file__).resolve().parent.parent / "main.py"


def isolated_environ(overrides: dict[str, str] | None = None) -> dict[str, str]:
    """開発者のシェルに設定された閾値（JA_GUARD_*）がテストの結果を変えないようにする。"""
    base = {key: value for key, value in os.environ.items() if not key.startswith("JA_GUARD_")}
    return {**base, **(overrides or {})}


def run_hook(
    payload: dict[str, object], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(ENTRY_POINT)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        env=isolated_environ(env),
        check=False,
    )


def stop_payload(response: str) -> dict[str, object]:
    return {
        "hook_event_name": "Stop",
        "stop_hook_active": False,
        "last_assistant_message": response,
    }


def test_english_response_writes_additional_context() -> None:
    result = run_hook(
        stop_payload("I have finished the refactoring and all tests are passing now.")
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"] == "Stop"


def test_output_is_readable_utf8() -> None:
    # 導入時の動作確認で人が読めるよう、日本語をエスケープせずに出力する
    result = run_hook(stop_payload("I have finished the refactoring and all tests pass now."))

    assert "日本語" in result.stdout.decode("utf-8")


def test_japanese_response_writes_nothing() -> None:
    result = run_hook(stop_payload("リファクタリングが終わり、テストもすべて通りました。"))

    assert result.returncode == 0
    assert result.stdout == b""


def test_closed_stdin_exits_without_error() -> None:
    # 標準入力が閉じていると sys.stdin は None になる
    result = subprocess.run(
        ["sh", "-c", f'"{sys.executable}" "{ENTRY_POINT}" <&-'],
        capture_output=True,
        env=isolated_environ(),
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == b""
    assert result.stderr == b""


def test_closed_stdout_exits_without_error() -> None:
    # 標準出力が閉じていると sys.stdout は None になる。差し戻す入力でも例外終了しない
    payload = json.dumps(stop_payload("I have finished the refactoring and all tests pass now."))
    result = subprocess.run(
        ["sh", "-c", f'"{sys.executable}" "{ENTRY_POINT}" >&-'],
        input=payload.encode("utf-8"),
        capture_output=False,
        stderr=subprocess.PIPE,
        env=isolated_environ(),
        check=False,
    )

    assert result.returncode == 0
    assert result.stderr == b""


def test_package_is_found_without_script_directory_on_path() -> None:
    # PYTHONSAFEPATH（3.11 以降）が有効でスクリプトのディレクトリが sys.path に入らなくても動く
    result = run_hook(
        stop_payload("I have finished the refactoring and all tests pass now."),
        env={"PYTHONSAFEPATH": "1"},
    )

    assert result.returncode == 0
    assert result.stderr == b""


def test_input_is_read_as_utf8_regardless_of_locale() -> None:
    # 標準入出力の既定の文字コードが ASCII の環境でも、日本語を含む入力で落ちない
    result = run_hook(
        stop_payload("I have finished the refactoring and updated the docs as well. 日本語。"),
        env={"PYTHONIOENCODING": "ascii"},
    )

    assert result.returncode == 0
    assert result.stderr == b""
    assert json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"] == "Stop"
