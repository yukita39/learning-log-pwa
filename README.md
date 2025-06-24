# 作業ログアプリ README

このドキュメントでは、本アプリケーションの概要、導入手順、実装済み機能、作成中の機能をまとめています。

---

## 1. 概要

フラスコ（Flask）で開発した「作業ログアプリ」です。
- 学習や作業内容を記録し、Google カレンダーに自動書き込み
- 学習時間の統計表示（継続日数、ストリーク、累計時間）
- タグ機能（ログにタグ付け、人気タグランキング、ダッシュボードで可視化）
- PWA（Progressive Web App）対応

将来的にはユーザーごとにログイン・個別カレンダー発行にも対応予定です。

---

## 2. 導入手順

### 2.1. リポジトリのクローン
```bash
git clone <リポジトリ URL>
cd learning-log-pwa
```

### 2.2. 仮想環境の作成と依存ライブラリのインストール
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2.3. 環境変数の設定
```dotenv
# .env ファイル例
SECRET_KEY=任意の文字列
DATABASE_URL=sqlite:///learning.db   # 開発用
CRED_PATH=client_secret.json          # Google OAuth
TOKEN_PATH=token.json                 # トークン保存先
SERVICE_CRED=service_account.json     # サービスアカウント鍵
CALENDAR_ID=primary                   # 書き込み先カレンダー
```

### 2.4. データベース初期化
```bash
# SQLite（開発用）
db.py を直接実行するか、alembic でマイグレーションを適用
python db.py  # Base.metadata.create_all()
# （または）
alembic upgrade head
```

### 2.5. アプリケーション起動
```bash
flask run
# または
python app.py
```
ブラウザで http://127.0.0.1:5000 にアクセスしてください。

---

## 3. 実装済み機能

- **ログ登録**：日付／開始時刻／内容／所要時間／感想／タグ を入力し保存
- **Google カレンダー連携**：ログ登録時に `#` を付与した件名で予定を追加
- **統計表示**：継続日数／ストリーク／累計学習時間を一覧表示
- **タグ機能**：
  - 入力補完（人気タグ取得 API 連携）
  - タグランキング TOP5 ページ
  - ダッシュボードで期間別・タグ別のグラフ可視化
- **PWA 化**：manifest.json と service-worker.js を配置し、デスクトップ／モバイルでインストール可能

---

## 4. 作成中の機能（# 作成中）

- ユーザー登録／認証機能  # 作成中
  - Flask-Login を使ったログイン・ログアウト、自分専用カレンダー発行
- 学習スケジュール自動作成機能  # 作成中
  - ChatGPT API 連携による翌日のタスク提案

---

## 5. デプロイ

- Render／Heroku などのクラウドサービスに対応
- 環境変数は管理画面から設定可能
- PostgreSQL への切り替え：`DATABASE_URL` を変更し、alembic でマイグレーション実行

---

## 6. 今後の拡張アイデア

- Slack 連携によるリマインダー通知
- 他サービス連携（Notion, Todoist など）
- モバイル専用 UI の改善
- オフライン時のログキャッシュ

---

※本 README の「作成中」セクションは実装が完了次第、削除または詳細化します。


Pull Request を送信

ライセンス

MIT

