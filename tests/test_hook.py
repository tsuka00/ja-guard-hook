from __future__ import annotations

import json
from typing import Any

import pytest

from ja_guard.hook import handle

ENGLISH_RESPONSE = (
    "I've updated the configuration file and added the missing tests. "
    "Let me know if you want me to run the full suite."
)
JAPANESE_RESPONSE = "設定ファイルを更新し、足りなかったテストを追加しました。"


def stop_input(**overrides: Any) -> str:
    payload: dict[str, Any] = {
        "session_id": "abc123",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/tmp",
        "hook_event_name": "Stop",
        "stop_hook_active": False,
        "last_assistant_message": ENGLISH_RESPONSE,
    }
    payload.update(overrides)
    return json.dumps(payload)


class TestSendBack:
    def test_english_response_is_sent_back_with_additional_context(self) -> None:
        output = handle(stop_input(), {})

        assert output is not None
        hook_output = json.loads(output)["hookSpecificOutput"]
        assert hook_output["hookEventName"] == "Stop"
        assert "日本語" in hook_output["additionalContext"]

    def test_output_does_not_use_decision_block(self) -> None:
        # decision: block は hook error として表示されるため使わない（docs/decisions/0004）
        output = handle(stop_input(), {})

        assert output is not None
        assert "decision" not in json.loads(output)


class TestPass:
    def test_japanese_response_passes(self) -> None:
        assert handle(stop_input(last_assistant_message=JAPANESE_RESPONSE), {}) is None

    def test_rewritten_response_passes_even_if_english(self) -> None:
        # 書き直しも英語だった場合に差し戻しを繰り返さない
        assert handle(stop_input(stop_hook_active=True), {}) is None

    def test_other_events_pass(self) -> None:
        assert handle(stop_input(hook_event_name="SubagentStop"), {}) is None

    @pytest.mark.parametrize("response", [None, 123, ["text"]])
    def test_non_string_response_passes(self, response: object) -> None:
        assert handle(stop_input(last_assistant_message=response), {}) is None

    def test_missing_response_passes(self) -> None:
        payload = json.loads(stop_input())
        del payload["last_assistant_message"]
        assert handle(json.dumps(payload), {}) is None

    @pytest.mark.parametrize("raw_input", ["", "not json", "[]", '"text"'])
    def test_malformed_input_passes(self, raw_input: str) -> None:
        assert handle(raw_input, {}) is None


class TestThresholdsFromEnvironment:
    def test_environment_thresholds_are_applied(self) -> None:
        assert handle(stop_input(), {"JA_GUARD_MIN_WORDS": "1000"}) is None
