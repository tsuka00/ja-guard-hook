"""判定のテスト。例文は、過去のセッションで実際に出た応答の形に合わせている。"""

from __future__ import annotations

import pytest

from ja_guard.detector import Thresholds, is_english_dominant


class TestEnglishResponses:
    @pytest.mark.parametrize(
        "text",
        [
            # バックグラウンドの処理を待つ間の報告。英語になりやすい
            "Tests are running in the background. The next step depends on the results, "
            "so I'm waiting until they come in.",
            "The fixes are committed (`abc1234`), and I'm now running another review "
            "on just that diff. I'll report once the result is in.",
        ],
    )
    def test_english_response_is_english(self, text: str) -> None:
        assert is_english_dominant(text)

    def test_english_response_quoting_japanese_is_english(self) -> None:
        text = (
            'The settings page is working: each item shows the "保存済み" (saved) label, '
            "and the counts per status are correct. Checking the remaining tabs next."
        )
        assert is_english_dominant(text)


class TestJapaneseResponses:
    @pytest.mark.parametrize(
        "text",
        [
            "設定ファイルを更新しました。次はテストを追加します。",
            # 英語の固有名詞・ファイル名・コマンドが多くても、会話は日本語
            "Amazon Bedrock AgentCore がいいと思います！",
            "detector.py と hook.py と config.py と main.py と test_hook.py を更新しました。",
            "CI の完了待ちです。通ったら PR をマージし、`Deploy` ワークフローの "
            "build → test → deploy を追います。",
        ],
    )
    def test_japanese_response_is_not_english(self, text: str) -> None:
        assert not is_english_dominant(text)

    def test_japanese_response_listing_urls_is_not_english(self) -> None:
        text = (
            "参考にしたページの URL です。\n\n"
            "- https://example.com/docs/getting-started\n"
            "- https://example.com/docs/configuration\n"
            "- https://example.com/docs/troubleshooting\n"
        )
        assert not is_english_dominant(text)

    def test_japanese_response_with_english_table_is_not_english(self) -> None:
        text = (
            "**users テーブルの例**です。列名は英語のままにしています。\n\n"
            "| id | user_name | display_name | created_at | updated_at |\n"
            "|---|---|---|---|---|\n"
            "| 1 | taro | 山田太郎 | 2026-01-01 | 2026-01-02 |\n"
        )
        assert not is_english_dominant(text)

    def test_short_english_response_is_ignored(self) -> None:
        assert not is_english_dominant("OK, done.")


class TestCode:
    def test_code_block_is_not_counted(self) -> None:
        text = (
            "次のコマンドで確認できます。\n"
            "```bash\n"
            "uv run pytest --verbose --capture=no tests/test_detector.py and more options\n"
            "```\n"
        )
        assert not is_english_dominant(text, Thresholds(min_words=1, ratio=0.01))

    def test_inline_code_is_not_counted(self) -> None:
        text = "`uv run pytest --verbose` を実行しました。"
        assert not is_english_dominant(text, Thresholds(min_words=1, ratio=0.01))


class TestJapaneseCharacters:
    @pytest.mark.parametrize("japanese", ["ひら", "カナ", "ｶﾅ", "漢字", "時々"])
    def test_japanese_characters_are_counted(self, japanese: str) -> None:
        # 英語の語2つに対して日本語2文字なら、1倍を超えない
        assert not is_english_dominant(f"ab cd {japanese}", Thresholds(min_words=1, ratio=1.0))

    def test_symbols_are_not_counted_as_japanese(self) -> None:
        assert is_english_dominant("ab cd 「」。、・", Thresholds(min_words=1, ratio=1.0))


class TestThresholds:
    def test_words_below_minimum_are_not_judged(self) -> None:
        assert not is_english_dominant("a b c d", Thresholds(min_words=5, ratio=3.0))

    def test_words_at_minimum_are_judged(self) -> None:
        assert is_english_dominant("a b c d e", Thresholds(min_words=5, ratio=3.0))

    def test_words_equal_to_ratio_are_not_english(self) -> None:
        # 英語の語6つ・日本語2文字で、ちょうど3倍
        assert not is_english_dominant("a b c d e f 日本", Thresholds(min_words=1, ratio=3.0))

    def test_words_exceeding_ratio_are_english(self) -> None:
        assert is_english_dominant("a b c d e f g 日本", Thresholds(min_words=1, ratio=3.0))
