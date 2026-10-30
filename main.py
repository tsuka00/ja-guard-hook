#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 tsuka00
"""ja-guard-hook のエントリーポイント。settings.json の hooks.Stop からこのファイルを呼ぶ。"""

import sys
from pathlib import Path


def _run() -> int:
    # PYTHONSAFEPATH 等でスクリプトのディレクトリが sys.path に入らない環境でも
    # ja_guard を import できるようにする
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ja_guard.hook import main

    return main()


if __name__ == "__main__":
    sys.exit(_run())
