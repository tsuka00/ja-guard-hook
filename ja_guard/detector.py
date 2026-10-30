"""応答が英語主体かを判定する。

空白で区切った語のうち英字を含む ASCII の語の数と、日本語の文字数を比べる。
英語になった応答は丸ごと英語になり、日本語の応答では英語の語が日本語の文字数を大きく下回るので、
応答全体での単純な比較で分けられる。コードは英語で書くのが当然なので数えない。
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    """英語主体とみなす閾値。"""

    # 英語の語がこれ未満の応答は判定しない（「OK」程度の短い返事を差し戻さないため）
    min_words: int = 5
    # 英語の語の数が日本語の文字数のこの倍を超えたら英語主体とみなす
    ratio: float = 1.5


DEFAULT_THRESHOLDS = Thresholds()

_FENCED_CODE = re.compile(r"^[ \t]*(`{3,}|~{3,}).*?^[ \t]*\1", re.MULTILINE | re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_LATIN = re.compile(r"[A-Za-z]")

# 句読点・括弧・中黒などの記号は日本語の文字として数えない（長音符は数える）
_JAPANESE = re.compile(
    "["
    "\u3005-\u3007"  # 々〆〇
    "\u3041-\u3096\u3099-\u309f"  # 平仮名
    "\u30a1-\u30fa\u30fc-\u30ff"  # 片仮名
    "\u3400-\u4dbf"  # CJK 統合漢字拡張 A
    "\u4e00-\u9fff"  # CJK 統合漢字
    "\uf900-\ufaff"  # CJK 互換漢字
    "\uff66-\uff9f"  # 半角片仮名
    "]"
)


def is_english_dominant(text: str, thresholds: Thresholds = DEFAULT_THRESHOLDS) -> bool:
    """英語の語が min_words 以上あり、かつ日本語の文字数の ratio 倍を超えるとき英語主体とみなす。"""
    prose = _INLINE_CODE.sub(" ", _FENCED_CODE.sub(" ", text))
    words = sum(1 for token in prose.split() if token.isascii() and _LATIN.search(token))
    japanese = len(_JAPANESE.findall(prose))
    return words >= thresholds.min_words and words > japanese * thresholds.ratio
