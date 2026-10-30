from __future__ import annotations

import pytest

from ja_guard.detector import Thresholds, is_english_dominant

# 文字数の境界だけを検証するための閾値
LOOSE = Thresholds(min_latin=1, ratio=1.0)


class TestTypicalResponses:
    def test_japanese_response_is_not_english(self) -> None:
        text = "設定ファイルを更新しました。次はテストを追加します。"
        assert not is_english_dominant(text)

    def test_english_response_is_english(self) -> None:
        text = (
            "I've updated the configuration file and added the missing tests. "
            "Let me know if you want me to run the full suite."
        )
        assert is_english_dominant(text)

    def test_japanese_with_technical_terms_is_not_english(self) -> None:
        text = (
            "ruff と mypy の設定を pyproject.toml に追加しました。"
            "CI では Python 3.9 から 3.13 まで pytest を回します。"
        )
        assert not is_english_dominant(text)

    def test_short_english_reply_is_ignored(self) -> None:
        assert not is_english_dominant("OK, done.")


class TestIgnoredSegments:
    @pytest.mark.parametrize("fence", ["```", "~~~"])
    def test_code_block_is_ignored(self, fence: str) -> None:
        text = (
            "次のコマンドで確認できます。\n"
            f"{fence}bash\n"
            "uv run pytest --verbose --capture=no tests/test_detector.py\n"
            f"{fence}\n"
        )
        assert not is_english_dominant(text)

    def test_japanese_inside_code_block_is_not_counted(self) -> None:
        text = (
            "Here is the updated configuration for the hook settings file.\n"
            "```json\n"
            '{"comment": "日本語のコメントがたくさん書かれている設定ファイルの例です"}\n'
            "```\n"
        )
        assert is_english_dominant(text)

    def test_inline_code_is_ignored(self) -> None:
        text = "`load_thresholds_from_environment` と `is_english_dominant` を直しました。"
        assert not is_english_dominant(text)

    def test_url_is_ignored(self) -> None:
        text = "詳細は https://code.claude.com/docs/en/hooks#stop-decision-control を参照。"
        assert not is_english_dominant(text)

    def test_file_path_is_ignored(self) -> None:
        text = "/Users/someone/projects/personal-verification/ja_guard/detector.py を更新。"
        assert not is_english_dominant(text)

    def test_email_address_is_ignored(self) -> None:
        text = "連絡先は someone.longname@example-company.co.jp です。"
        assert not is_english_dominant(text)


class TestJapaneseCharacters:
    @pytest.mark.parametrize(
        "japanese",
        [
            "ひら",  # 平仮名
            "カナ",  # 片仮名
            "ｶﾅ",  # 半角片仮名
            "漢字",  # CJK 統合漢字
            "時々",  # 踊り字
            "ㇰ㐂",  # 片仮名拡張・CJK 統合漢字拡張 A
        ],
    )
    def test_japanese_characters_are_counted(self, japanese: str) -> None:
        # 英字2文字に対して日本語2文字なら、比率1倍を超えない
        assert not is_english_dominant(f"ab {japanese}", LOOSE)

    def test_symbols_are_not_counted_as_japanese(self) -> None:
        assert is_english_dominant("ab 「」。、・", LOOSE)


class TestThresholds:
    def test_latin_below_minimum_is_not_judged(self) -> None:
        assert not is_english_dominant("abcd", Thresholds(min_latin=5, ratio=3.0))

    def test_latin_at_minimum_is_judged(self) -> None:
        assert is_english_dominant("abcde", Thresholds(min_latin=5, ratio=3.0))

    def test_latin_equal_to_ratio_is_not_english(self) -> None:
        # 英字6文字・日本語2文字で、ちょうど3倍
        assert not is_english_dominant("abcdef 日本", Thresholds(min_latin=1, ratio=3.0))

    def test_latin_exceeding_ratio_is_english(self) -> None:
        assert is_english_dominant("abcdefg 日本", Thresholds(min_latin=1, ratio=3.0))
