---
status: accepted
date: 2026-10-30
decision-makers: tsuka00
---

# 最終応答だけを検査し、additionalContext で書き直させる

## 背景と課題

Stop hook で何を検査し、英語主体だったときにどう書き直させるかを決める必要がある。Claude Code の Stop hook には次の性質がある（公式ドキュメント hooks の Stop 節、CHANGELOG で確認）。

- 入力の `last_assistant_message` に最終応答の本文が入る（v2.1.47 以降）
- transcript は非同期に書かれ、Stop の時点で最終応答が含まれている保証がない
- 出力は `decision: "block"` と `hookSpecificOutput.additionalContext`（v2.1.163 以降）の2通り。後者は hook error として表示されない
- どちらの出力でも `stop_hook_active` と連続8回の上限によるループ防止が効く

## 判断基準

- 検出が確実であること（タイミングに依存しない）
- 実装が小さく、検証しやすいこと
- 利用者に誤解を与える表示（エラー扱い）を出さないこと

## 検討した選択肢

検査の対象:

1. 最終応答（`last_assistant_message`）だけ
2. 最終応答に加え、transcript からツール呼び出しの間の途中報告も読む

差し戻しの出力:

A. `hookSpecificOutput.additionalContext`
B. `decision: "block"` と `reason`

## 決定

1 と A を採る。

### 影響

- 良い: transcript の解析・書き込み待ちが不要で、判定が入力1つで閉じる。表示が「Stop hook feedback」になり、エラーに見えない
- 悪い: 途中報告が英語でも検出しない。Claude Code v2.1.163 未満では動かない（README に動作要件として書く）
- 途中報告の検査が必要になったら、transcript を読むモジュールを追加する。判定（`detector`）は入力の文字列だけを受けるので変更しない

### 確認方法

英語主体の `last_assistant_message` を与えると `additionalContext` を含む JSON を出力し、`stop_hook_active` が `true` のときは何も出力しないことをテストで確かめる。

## 選択肢ごとの長所・短所

### 1. 最終応答だけ

- 良い: 公式が案内する読み方で、タイミングに依存しない
- 悪い: 途中報告を見ない

### 2. 途中報告も読む

- 良い: 検出範囲が広い
- 悪い: transcript の形式（非公開）に依存し、書き込みの遅れを待つ処理が要る

### A. additionalContext

- 良い: 設計どおりの指示として扱われ、エラー表示にならない
- 悪い: v2.1.163 以上が必要

### B. decision: block

- 良い: 古いバージョンでも動く
- 悪い: 意図どおりの動作なのに hook error として表示される
