# Rule

このプロジェクト固有の絶対ルール。プロジェクト CLAUDE.md から @import されるため常時読み込まれる。

- 公開リポジトリとして第三者が読む前提で書く。コード・コメント・README・docs に、参考にした他者のリポジトリや作者への言及を入れない
- 実行時のコード（`ja_guard/` とエントリーポイント）は Python 3.9 以上の標準ライブラリだけで書く。サードパーティのパッケージは開発用（dev 依存）に限る
- 標準入出力と環境変数は `ja_guard/hook.py` だけが扱う。`sys.stdin` / `sys.stdout` / `sys.stderr`（`__stdin__` 等を含む）・`print`・`os.environ` / `os.environb` / `os.getenv` / `os.getenvb` は ruff の TID251・T20 で禁止済み
- 組み込みの `input` と `open` は ruff で禁止できない。実行時のコードでは使わず、レビューで確認する

## 用語集

| 呼び方 | 識別子 | 意味 | 使わない言い方 |
|---|---|---|---|
| 応答 | `response` | Claude がユーザーに出す本文 | message / reply |
| 英語主体 | `is_english_dominant` | 判定の結果 | — |
| 差し戻し | `additionalContext` | 書き直しを求めてターンを続けさせること（docs/decisions/0004） | reject / retry / block |
| ターン | `turn` | ユーザーの1発言から Claude の終了まで | — |

## コミットの scope

- `detector` / `hook` / `config` / `ci`
