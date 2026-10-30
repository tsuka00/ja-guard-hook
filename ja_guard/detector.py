"""応答が英語主体かを判定する。

英単語の数と日本語の文字数を比べる。英単語1語は数文字からなるので、英字の数で比べると
技術用語の多い日本語の応答まで英語主体と判定してしまう。

コード・URL・メールアドレス・ファイルパスは英語の文章ではないので数えない。
日本語の応答でも、英語のコマンドや識別子を見せるのは正当な使い方のため。
除外の正規表現は、トークンの途中から照合を始めないよう否定の後読みで始点を区切りの直後に限る。
始点を限らないと、区切りのない長い英数字列（ハッシュ・minify 済みのコード等）で
照合が2乗の時間になる。
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    """英語主体とみなす閾値。"""

    # 英単語がこれ未満の応答は判定しない（「OK」程度の短い返事を差し戻さないため）
    min_words: int = 5
    # 英単語の数が日本語の文字数のこの倍を超えたら英語主体とみなす
    ratio: float = 1.5


DEFAULT_THRESHOLDS = Thresholds()

# 行頭（字下げ可）の開きフェンス。バッククォートのフェンスは情報文字列にバッククォートを含まない
_FENCE_OPEN = re.compile(r"(`{3,})[^`]*$|(~{3,})")
# 同じ長さのバッククォートの連なりで囲んだインラインコード（CommonMark の code span）
_INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)[^\n]+?(?<!`)\1(?!`)")
_URL = re.compile(r"(?<![A-Za-z0-9+.-])[A-Za-z][A-Za-z0-9+.-]*://[\w\-.~:/?#@!$&*+;=%]+", re.ASCII)
# \w が日本語に一致しないよう ASCII に限る
_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.ASCII)
_PATH_CANDIDATE = re.compile(r"(?<![\w.~/-])[\w.~-]*(?:/[\w.~-]*)+", re.ASCII)

_ENGLISH_WORD = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*")

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
    "\U00020000-\U0003347f"  # CJK 統合漢字拡張 B〜J
    "]"
)


def is_english_dominant(text: str, thresholds: Thresholds = DEFAULT_THRESHOLDS) -> bool:
    """英単語が min_words 以上あり、かつ日本語の文字数の ratio 倍を超えるとき英語主体とみなす。"""
    prose = _strip_ignored(text)
    words = len(_ENGLISH_WORD.findall(prose))
    japanese = len(_JAPANESE.findall(prose))
    return words >= thresholds.min_words and words > japanese * thresholds.ratio


def _strip_ignored(text: str) -> str:
    text = _strip_fenced_code(text)
    for pattern in (_INLINE_CODE, _URL, _EMAIL):
        text = pattern.sub(" ", text)
    return _PATH_CANDIDATE.sub(_strip_if_path, text)


def _strip_fenced_code(text: str) -> str:
    """閉じたコードブロックを除く。閉じていないフェンスは、文中で ``` に触れただけの
    可能性があるので文章として残す。正規表現でなく行単位で走査し、線形時間で終わらせる。"""
    kept: list[str] = []
    open_block: list[str] = []
    fence = ""
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not fence:
            opening = _FENCE_OPEN.match(stripped)
            if opening:
                fence = opening.group(1) or opening.group(2)
                open_block = [line]
            else:
                kept.append(line)
            continue
        open_block.append(line)
        # 閉じフェンスは同じ文字で、開きと同じ長さ以上の連なりだけの行
        if len(stripped) >= len(fence) and set(stripped) == {fence[0]}:
            kept.append("\n")
            open_block = []
            fence = ""
    return "".join(kept + open_block)


def _strip_if_path(match: re.Match[str]) -> str:
    return " " if _looks_like_path(match.group().rstrip(".")) else match.group()


def _looks_like_path(token: str) -> bool:
    """and/or のようなスラッシュ区切りの英単語は文章として数え、パスらしい形だけを除外する。"""
    return token.startswith(("/", "~", ".")) or token.endswith("/") or "." in token or "_" in token
