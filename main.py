#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 tsuka00
"""ja-guard-hook のエントリーポイント。settings.json の hooks.Stop からこのファイルを呼ぶ。"""

import sys

from ja_guard.hook import main

if __name__ == "__main__":
    sys.exit(main())
