"""環境変数から閾値を読む。"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import TypeVar

from ja_guard.detector import DEFAULT_THRESHOLDS, Thresholds

MIN_WORDS_ENV = "JA_GUARD_MIN_WORDS"
RATIO_ENV = "JA_GUARD_RATIO"

_Number = TypeVar("_Number", int, float)


def load_thresholds(environ: Mapping[str, str]) -> Thresholds:
    """不正な値は既定値に戻す。設定の誤りで例外終了すると、検査そのものが働かなくなるため。"""
    return Thresholds(
        min_words=_parse_positive(environ.get(MIN_WORDS_ENV), int, DEFAULT_THRESHOLDS.min_words),
        ratio=_parse_positive(environ.get(RATIO_ENV), float, DEFAULT_THRESHOLDS.ratio),
    )


def _parse_positive(
    value: str | None, convert: Callable[[str], _Number], default: _Number
) -> _Number:
    if value is None:
        return default
    try:
        parsed = convert(value)
        # float に変換できない大きさの int では isfinite が OverflowError を投げる
        is_usable = math.isfinite(parsed) and parsed > 0
    except (ValueError, OverflowError):
        return default
    return parsed if is_usable else default
