# Discord業務ハブBot

Discordを窓口として、利用者ごとの対話、要点整理、タスク管理、メール補助、PDF出力を行う業務支援Botです。

会話内容を整理し、必要に応じて Trello や Gmail と連携できます。  
将来的には他ツールも追加できる、拡張前提の構成を想定しています。

---

## 目次

- [概要](#概要)
- [特徴](#特徴)
- [想定ユースケース](#想定ユースケース)
- [MVP範囲](#mvp範囲)
- [主な機能](#主な機能)
- [コマンド例](#コマンド例)
- [Discord構成イメージ](#discord構成イメージ)
- [システム構成](#システム構成)
- [開発予定](#開発予定)
- [Issue候補](#issue候補)
- [ディレクトリ構成例](#ディレクトリ構成例)
- [開発の進め方](#開発の進め方)
- [ドキュメント](#ドキュメント)
- [今後の拡張](#今後の拡張)
- [備考](#備考)

---

## 概要

本Botは、Discordを主要な操作画面として利用する業務ハブです。

単なる会話Botではなく、以下を一つの窓口に集約します。

- 利用者ごとの対話窓口
- 要点整理
- タスク管理
- 決定事項管理
- 重要リンク保存
- Gmail連携
- Trello連携
- PDF出力
- 将来の外部ツール追加

---

## 特徴

- 利用者ごとの専用窓口で対話できる
- 会話内容から要点・タスク・決定事項・重要リンクを整理できる
- 対話結果や整理結果をPDFとして出力できる
- Discordから Trello / Gmail を操作できる
- 外部ツール側の更新内容もDiscordで確認できる
- 将来的に他ツールを追加しやすい

---

## 想定ユースケース

- Discord上の相談内容が流れて埋もれるのを防ぎたい
- 会話内容をそのままタスクや記録に変えたい
- 利用者ごとに相談窓口を分けたい
- 結果をPDFで保管・共有したい
- Discordを業務の入口として使いたい

---

## MVP範囲

まず最初に作る最小構成は以下を対象とします。

### MVPで実装するもの
- 利用者ごとの専用窓口作成
- slash command による基本操作
- 当日要約機能
- タスク追加機能
- 決定事項保存機能
- 重要リンク保存機能
- PDF出力機能
- コンテキストクリア機能

### MVPではまだ対象外にするもの
- Gmail双方向同期の完全対応
- Trelloの高度な状態同期
- Notion / GitHub / Google Drive 連携
- 外部Web管理画面
- 高度な検索機能
- 契約・請求管理機能

### MVPのゴール
Discordだけで以下が回ることを最初の完成条件とします。

1. 利用者専用窓口を開ける  
2. 対話内容を整理できる  
3. タスクや決定事項を保存できる  
4. 結果をPDFで出力できる

---

## 主な機能

### 窓口機能
- 利用者ごとの専用窓口作成
- 対話単位での情報整理
- 窓口ごとの状態管理

### 整理機能
- 要点抽出
- タスク抽出
- 決定事項整理
- 重要リンク保存

### 出力機能
- PDF出力
- 要約表示
- タスク一覧表示

### 外部連携
- Trelloカード作成・更新
- Gmail下書き作成・送信補助
- 将来の外部ツール追加

---

## コマンド例

### 窓口管理
- `/session-open`
- `/session-close`
- `/session-clear`

### 整理・出力
- `/summary-today`
- `/pdf-export`
- `/link-save`
- `/decision-add`

### タスク管理
- `/task-add`
- `/task-list`
- `/task-move`
- `/task-done`

### Gmail連携
- `/mail-draft`
- `/mail-send`

### Trello連携
- `/trello-add`
- `/trello-move`
- `/trello-comment`

---

## Discord構成イメージ

### 推奨チャンネル
- `#窓口-受付`
- `#bot-commands`
- `#daily-summary`
- `#決定事項`
- `#重要リンク`
- `#運営ログ`
- `#障害通知`

### 窓口方式
以下のいずれかを想定します。

1. 利用者ごとの専用チャンネル  
2. 受付チャンネル配下の専用 private thread（推奨）

---

## システム構成

本システムは、Discordを入口としつつ、中央ハブ方式で構成します。

### 基本構成
- **Discord**: 利用者との対話窓口、コマンド操作画面
- **業務ハブAPI**: コマンド処理、要約処理、外部連携の中核
- **Database**: 利用者、窓口、要点、タスク、連携ID等を保存
- **Connector**: Trello、Gmail、将来追加する外部ツール連携
- **PDF生成機能**: 対話結果や整理結果のPDF生成

### 設計方針
- Discordを主操作画面とする
- 中央ハブでデータを一元管理する
- 外部ツールは connector 方式で追加する
- 会話ログそのものと、整理済み情報を分けて扱う
- 双方向同期を前提にする

---

## 開発予定

### Phase 1: MVP
- 窓口作成
- slash command 基本機能
- 要約
- タスク保存
- 決定事項保存
- 重要リンク保存
- PDF出力
- コンテキストクリア

### Phase 2: 外部連携強化
- Trello連携
- Gmail下書き連携
- 監査ログ強化
- 基本双方向同期

### Phase 3: 運用強化
- Gmail更新取り込み
- 他ツール connector 追加
- 高度なワークフロー機能
- 運営向け管理機能

### Phase 4: 拡張
- 検索性強化
- ダッシュボード表示
- Web管理画面
- 複数PDFテンプレート
- 契約・案件管理機能

---

## Issue候補

初期の Issue は次のように切ることを想定します。

### 優先度: 高
- [ ] Discord bot の基本セットアップ
- [ ] `/session-open` 実装
- [ ] `/session-clear` 実装
- [ ] `/summary-today` 実装
- [ ] `/task-add` 実装
- [ ] `/decision-add` 実装
- [ ] `/link-save` 実装
- [ ] `/pdf-export` 実装
- [ ] 利用者ごとの窓口権限制御
- [ ] Session / Task / Decision / Link のDB設計

### 優先度: 中
- [ ] `/task-list` 実装
- [ ] `/task-move` 実装
- [ ] `/task-done` 実装
- [ ] PDFテンプレート初版作成
- [ ] 監査ログ保存
- [ ] エラーハンドリング共通化
- [ ] Discordメッセージ参照保存

### 優先度: 低
- [ ] `/mail-draft` 実装
- [ ] `/mail-send` 実装
- [ ] `/trello-add` 実装
- [ ] `/trello-move` 実装
- [ ] `/trello-comment` 実装
- [ ] Gmail同期処理
- [ ] Trello同期処理
- [ ] 外部ツール connector 抽象化

---

## ディレクトリ構成例

```text
project-root/
├─ README.md
├─ docs/
│  └─ spec.md
├─ src/
│  ├─ commands/
│  ├─ services/
│  ├─ connectors/
│  ├─ models/
│  ├─ repositories/
│  ├─ pdf/
│  ├─ utils/
│  └─ main.*
├─ tests/
├─ .env.example
└─ package.json or pyproject.toml