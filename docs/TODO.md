# TODO

- [ ] GitHub Actions CI を整える（2026-10-30）
- [ ] TDD で `config`（環境変数から閾値を読む）を作る（2026-10-30）
- [ ] TDD で `detector`（除外処理・閾値・日本語の文字範囲）を作る（2026-10-30）
- [ ] TDD で `hook`（`stop_hook_active` によるループ防止を含む）とエントリーポイントを作る（2026-10-30）
- [ ] 手元の `~/.claude/hooks/` に入れて、英語の応答が差し戻されることを確かめる（2026-10-30）
- [ ] README（仕組み・入れ方・設定・制約・動作要件 v2.1.163 以上）を書く（2026-10-30）
- [ ] walking skeleton が通ったら /arch-doc generate で C4 図（docs/architecture/）を作る（2026-10-30）

## 完了済み

- [x] プロジェクトセットアップ完了を確認する（2026-10-30）
- [x] pyproject・ruff・mypy・pytest を整える（2026-10-30）
- [x] 公式ドキュメントで Stop hook の入出力を確認する → docs/decisions/0004（2026-10-30）
- [x] 途中報告を検査対象にするか決める → 対象外（docs/decisions/0004）（2026-10-30）
