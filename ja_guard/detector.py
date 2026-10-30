"""応答が英語主体かを判定する。

コード・URL・メールアドレス・ファイルパスは英語の文章ではないので数えない。
日本語の応答でも、英語のコマンドや識別子を見せるのは正当な使い方のため。
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    """英語主体とみなす閾値。"""

    # 英字がこれ未満の応答は判定しない（「OK」程度の短い返事を差し戻さないため）
    min_latin: int = 25
    # 英字の数が日本語の文字数のこの倍を超えたら英語主体とみなす
    ratio: float = 3.0


DEFAULT_THRESHOLDS = Thresholds()

_IGNORED_PATTERNS: tuple[re.Pattern[str], ...] = (
    # フェンスで囲んだコードブロック。閉じ忘れは末尾までをコードとみなす
    re.compile(r"(```|~~~)[\s\S]*?(?:\1|\Z)"),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[!-~]+"),
    # \w が日本語に一致しないよう ASCII に限る
    re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.ASCII),
    re.compile(r"[\w.~-]*(?:/[\w.~-]+)+/?", re.ASCII),
)

_LATIN = re.compile(r"[A-Za-z]")

# 句読点・括弧・中黒などの記号は日本語の文字として数えない（長音符は数える）
_JAPANESE = re.compile(
    "["
    "\u3005-\u3007"  # 々〆〇
    "\u3041-\u3096\u3099-\u309f"  # 平仮名
    "\u30a1-\u30fa\u30fc-\u30ff"  # 片仮名
    "\u31f0-\u31ff"  # 片仮名拡張
    "\u3400-\u4dbf"  # CJK 統合漢字拡張 A
    "\u4e00-\u9fff"  # CJK 統合漢字
    "\uf900-\ufaff"  # CJK 互換漢字
    "\uff66-\uff9f"  # 半角片仮名
    "]"
)


def is_english_dominant(text: str, thresholds: Thresholds = DEFAULT_THRESHOLDS) -> bool:
    """英字が min_latin 以上あり、かつ日本語の文字数の ratio 倍を超えるとき英語主体とみなす。"""
    prose = _strip_ignored(text)
    latin = len(_LATIN.findall(prose))
    japanese = len(_JAPANESE.findall(prose))
    return latin >= thresholds.min_latin and latin > japanese * thresholds.ratio


def _strip_ignored(text: str) -> str:
    for pattern in _IGNORED_PATTERNS:
        text = pattern.sub(" ", text)
    return text
