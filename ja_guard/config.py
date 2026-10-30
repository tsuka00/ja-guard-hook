"""環境変数から閾値を読む。"""

from __future__ import annotations

import math
from collections.abc import Mapping

from ja_guard.detector import DEFAULT_THRESHOLDS, Thresholds

MIN_LATIN_ENV = "JA_GUARD_MIN_LATIN"
RATIO_ENV = "JA_GUARD_RATIO"


def load_thresholds(environ: Mapping[str, str]) -> Thresholds:
    """不正な値は既定値に戻す。設定の誤りで例外終了すると、検査そのものが働かなくなるため。"""
    return Thresholds(
        min_latin=_parse_positive_int(environ.get(MIN_LATIN_ENV), DEFAULT_THRESHOLDS.min_latin),
        ratio=_parse_positive_float(environ.get(RATIO_ENV), DEFAULT_THRESHOLDS.ratio),
    )


def _parse_positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _parse_positive_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError:
        return default
    return parsed if math.isfinite(parsed) and parsed > 0 else default
