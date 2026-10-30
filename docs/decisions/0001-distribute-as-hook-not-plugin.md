---
status: accepted
date: 2026-10-30
decision-makers: tsuka00
---

# hook として配置し、Plugin では配らない

## 背景と課題

ja-guard-hook を公開リポジトリで配る。利用者の環境に入れる方法として、Claude Code Plugin として配るか、`~/.claude/hooks/` に置いて settings.json に登録する hook として配るかを決める必要がある。

## 判断基準

- 利用者が何が入るかを把握しやすいこと
- 判定・解析・入出力をモジュールに分けた構造を保てること
- 更新・削除の手順が単純であること

## 検討した選択肢

1. `git clone` で `~/.claude/hooks/ja-guard-hook/` に置き、settings.json の `hooks.Stop` に登録する
2. 単一ファイルを curl で `~/.claude/hooks/` に取得し、settings.json に登録する
3. Claude Code Plugin として marketplace 経由で配る

## 決定

選択肢 1 を採る。hook として配置したいという方針に沿い、かつリポジトリの構造をそのまま使えるため。

### 影響

- 良い: モジュールに分けた構造のまま動かせる。更新は `git pull`、削除はディレクトリと設定行を消すだけ
- 悪い: 利用者が settings.json を自分で編集する必要がある。README に貼り付け用の JSON と確認手順を載せて補う

### 確認方法

README の手順だけで、空の `~/.claude/hooks/` から導入して英語の応答が差し戻されることを確かめる。

## 選択肢ごとの長所・短所

### 1. git clone で配置

- 良い: 構造を分けたまま配れる。`git pull` で更新できる
- 悪い: テストなど実行に不要なファイルも手元に入る

### 2. 単一ファイルを curl で取得

- 良い: 入るファイルが1つで最小
- 悪い: 判定・解析・入出力を1ファイルに詰めることになり、構造を分けられない。更新は再取得

### 3. Plugin

- 良い: `/plugin` から導入・更新・削除が一括ででき、settings.json を触らない
- 悪い: hook として配置したいという方針に合わない
