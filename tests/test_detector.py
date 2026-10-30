from __future__ import annotations

import time

import pytest

from ja_guard.detector import Thresholds, is_english_dominant

# 英単語が1語でも残れば英語主体と判定する閾値。除外の漏れを検出するために使う
STRICT = Thresholds(min_words=1, ratio=0.01)
# 英単語と日本語が同数なら英語主体としない閾値。日本語の文字の数え方を検証するために使う
EVEN = Thresholds(min_words=1, ratio=1.0)


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

    def test_english_with_a_few_japanese_words_is_english(self) -> None:
        text = "I updated the 設定 file and confirmed that all tests pass."
        assert is_english_dominant(text)

    @pytest.mark.parametrize(
        "text",
        [
            "ruff と mypy の設定を pyproject.toml に追加しました。",
            "Next.js の App Router で Server Components と Client Components を使い分けます。",
            "エラーは TypeError: Cannot read properties of undefined (reading 'map') です。",
            "原因は ModuleNotFoundError: No module named 'ja_guard' でした。",
        ],
    )
    def test_japanese_with_technical_terms_is_not_english(self, text: str) -> None:
        assert not is_english_dominant(text)

    def test_short_english_reply_is_ignored(self) -> None:
        assert not is_english_dominant("OK, done.")


class TestIgnoredSegments:
    @pytest.mark.parametrize("fence", ["```", "~~~", "````"])
    def test_code_block_is_ignored(self, fence: str) -> None:
        text = f"次のとおりです。\n{fence}bash\nuv run pytest --verbose\n{fence}\n"
        assert not is_english_dominant(text, STRICT)

    def test_indented_code_block_is_ignored(self) -> None:
        text = "1. 次のとおりです。\n   ```bash\n   uv run pytest --verbose\n   ```\n"
        assert not is_english_dominant(text, STRICT)

    def test_code_block_closed_by_longer_fence_is_ignored(self) -> None:
        text = "次のとおりです。\n```\nuv run pytest --verbose\n````\n以上です。"
        assert not is_english_dominant(text, STRICT)

    def test_japanese_inside_code_block_is_not_counted(self) -> None:
        text = (
            "Here is the updated configuration for the hook settings file.\n"
            "```json\n"
            '{"comment": "日本語のコメントがたくさん書かれている設定ファイルの例です"}\n'
            "```\n"
        )
        assert is_english_dominant(text)

    @pytest.mark.parametrize(
        "code",
        ["`is_english_dominant`", "``load_thresholds``", "``code with ` inside``"],
    )
    def test_inline_code_is_ignored(self, code: str) -> None:
        assert not is_english_dominant(f"{code} を直しました。", STRICT)

    @pytest.mark.parametrize(
        "url",
        [
            "https://code.claude.com/docs/en/hooks#stop-decision-control",
            "https://example.com/search?q=hook&lang=ja",
        ],
    )
    def test_url_is_ignored(self, url: str) -> None:
        assert not is_english_dominant(f"詳細は {url} を参照。", STRICT)

    def test_email_address_is_ignored(self) -> None:
        assert not is_english_dominant("連絡先は someone@example.co.jp です。", STRICT)

    @pytest.mark.parametrize(
        "path",
        [
            "/Users/someone/projects/ja_guard/detector.py",
            "~/.claude/hooks/ja-guard-hook/main.py",
            "./scripts/check.sh",
            "ja_guard/detector.py",
            "docs/decisions/",
        ],
    )
    def test_file_path_is_ignored(self, path: str) -> None:
        assert not is_english_dominant(f"{path} を更新しました。", STRICT)


class TestCountedSegments:
    """除外の対象に似ているが、英語の文章として数えるべきもの。"""

    def test_backticks_inside_sentence_do_not_hide_following_text(self) -> None:
        text = (
            "Use ``` to open a fenced block. Then I refactored the whole module "
            "and all the tests pass now."
        )
        assert is_english_dominant(text)

    def test_text_after_longer_closing_fence_is_counted(self) -> None:
        text = "```\nuv run pytest\n````\nI refactored the whole module and all tests pass now."
        assert is_english_dominant(text)

    def test_unclosed_fence_does_not_hide_following_text(self) -> None:
        text = "```\nis the fence marker. I refactored the whole module and all tests pass now."
        assert is_english_dominant(text)

    def test_double_backticks_do_not_pair_with_later_inline_code(self) -> None:
        text = "``foo`` I refactored the whole module and all the tests pass now so `x` is fine"
        assert is_english_dominant(text)

    def test_word_right_after_url_is_counted(self) -> None:
        assert is_english_dominant("詳細は (https://example.com/docs)and を参照。", STRICT)

    def test_slash_separated_words_are_counted(self) -> None:
        assert is_english_dominant("Updated input/output, read/write and client/server handling.")


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
            "𠮷𩸽",  # CJK 統合漢字拡張 B
            "𱍐𱍑",  # CJK 統合漢字拡張 H
        ],
    )
    def test_japanese_characters_are_counted(self, japanese: str) -> None:
        # 英単語2語に対して日本語2文字なら、1倍を超えない
        assert not is_english_dominant(f"ab cd {japanese}", EVEN)

    def test_symbols_are_not_counted_as_japanese(self) -> None:
        assert is_english_dominant("ab cd 「」。、・", EVEN)


class TestThresholds:
    def test_words_below_minimum_are_not_judged(self) -> None:
        assert not is_english_dominant("a b c d", Thresholds(min_words=5, ratio=3.0))

    def test_words_at_minimum_are_judged(self) -> None:
        assert is_english_dominant("a b c d e", Thresholds(min_words=5, ratio=3.0))

    def test_words_equal_to_ratio_are_not_english(self) -> None:
        # 英単語6語・日本語2文字で、ちょうど3倍
        assert not is_english_dominant("a b c d e f 日本", Thresholds(min_words=1, ratio=3.0))

    def test_words_exceeding_ratio_are_english(self) -> None:
        assert is_english_dominant("a b c d e f g 日本", Thresholds(min_words=1, ratio=3.0))


class TestPerformance:
    @pytest.mark.parametrize("unit", ["a", "a.", "a@", "a:/", "a/", "a`", "``a", "```a\n"])
    def test_long_unbroken_text_is_judged_in_linear_time(self, unit: str) -> None:
        # ハッシュや minify 済みのコードのような区切りのない文字列でも、Stop を待たせない
        text = unit * (50_000 // len(unit))

        started = time.perf_counter()
        is_english_dominant(text)

        assert time.perf_counter() - started < 1.0
