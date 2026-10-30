from __future__ import annotations

import pytest

from ja_guard.config import load_thresholds
from ja_guard.detector import DEFAULT_THRESHOLDS, Thresholds


def test_defaults_are_used_without_environment_variables() -> None:
    assert load_thresholds({}) == DEFAULT_THRESHOLDS


def test_environment_variables_override_defaults() -> None:
    environ = {"JA_GUARD_MIN_WORDS": "8", "JA_GUARD_RATIO": "2.5"}
    assert load_thresholds(environ) == Thresholds(min_words=8, ratio=2.5)


def test_surrounding_whitespace_is_allowed() -> None:
    environ = {"JA_GUARD_MIN_WORDS": " 8 ", "JA_GUARD_RATIO": " 2.5\n"}
    assert load_thresholds(environ) == Thresholds(min_words=8, ratio=2.5)


@pytest.mark.parametrize("value", ["", "abc", "0", "-1", "2.5"])
def test_invalid_min_words_falls_back_to_default(value: str) -> None:
    thresholds = load_thresholds({"JA_GUARD_MIN_WORDS": value, "JA_GUARD_RATIO": "2.5"})
    assert thresholds == Thresholds(min_words=DEFAULT_THRESHOLDS.min_words, ratio=2.5)


def test_too_large_min_words_falls_back_to_default() -> None:
    # float に変換できない大きさの整数でも例外にしない
    thresholds = load_thresholds({"JA_GUARD_MIN_WORDS": "1" + "0" * 400})
    assert thresholds.min_words == DEFAULT_THRESHOLDS.min_words


@pytest.mark.parametrize("value", ["", "abc", "0", "-1", "nan", "inf"])
def test_invalid_ratio_falls_back_to_default(value: str) -> None:
    thresholds = load_thresholds({"JA_GUARD_MIN_WORDS": "8", "JA_GUARD_RATIO": value})
    assert thresholds == Thresholds(min_words=8, ratio=DEFAULT_THRESHOLDS.ratio)
