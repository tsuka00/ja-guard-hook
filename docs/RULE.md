# Rule

このプロジェクト固有の絶対ルール。プロジェクト CLAUDE.md から @import されるため常時読み込まれる。

- 公開リポジトリとして第三者が読む前提で書く。コード・コメント・README・docs に、参考にした他者のリポジトリや作者への言及を入れない
- 実行時のコード（`ja_guard/` とエントリーポイント）は Python 3.9 以上の標準ライブラリだけで書く。サードパーティのパッケージは開発用（dev 依存）に限る
- 判定ロジック（`detector`）は I/O を持たない純関数にする。ファイル・stdin/stdout・環境変数の読み取りは `transcript` / `hook` / `config` に閉じ込める

## 用語集

| 呼び方 | 識別子 | 意味 | 使わない言い方 |
|---|---|---|---|
| 応答 | `response` | Claude がユーザーに出す本文 | message / reply |
| 英語主体 | `is_english_dominant` | 判定の結果 | — |
| 差し戻し | `block` | Stop を止めて書き直させること | reject / retry |
| ターン | `turn` | ユーザーの1発言から Claude の終了まで | — |

## コミットの scope

- `detector` / `transcript` / `hook` / `config` / `ci`
