# 📚 Learning Log PWA - 学習記録管理アプリケーション

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

学習の進捗を記録し、Google カレンダーと連携できる Progressive Web App (PWA) です。  
日々の学習を可視化し、モチベーション維持をサポートします。

## 🌟 主な機能

### 📝 学習ログ管理
- **簡単記録**: 日付、時間、内容、感想をフォームから簡単入力
- **タグ機能**: 学習内容をタグで分類・整理
- **よく使うタグ**: 頻繁に使用するタグをワンクリックで追加

### 📊 統計・可視化
- **学習統計**: 総学習時間、継続日数、連続記録日数を表示
- **ダッシュボード**: Chart.jsを使用した美しいグラフで進捗を可視化
  - 日別・週別・月別の学習時間推移
  - タグ別の学習時間分布
- **タグランキング**: よく使うタグTOP5を表示

### 📅 Google カレンダー連携
- **自動記録**: 学習ログを自動的にGoogleカレンダーに追加
- **プライバシー重視**: ユーザーが明示的に設定した場合のみ連携
- **柔軟な設定**: 個人のカレンダーIDを設定可能

### 🔐 セキュリティ
- **ユーザー認証**: Flask-Loginによる安全な認証システム
- **パスワード保護**: Werkzeugによるハッシュ化
- **セッション管理**: HTTPOnly、Secure、SameSiteクッキー設定

### 📱 PWA対応
- **オフライン対応**: Service Workerによるキャッシュ機能
- **インストール可能**: デスクトップ・モバイルにアプリとしてインストール
- **レスポンシブデザイン**: Bootstrap 5による美しいUI

## 🚀 技術スタック

### バックエンド
- **言語**: Python 3.11
- **フレームワーク**: Flask 2.3.3
- **ORM**: SQLAlchemy 1.4
- **認証**: Flask-Login
- **フォーム**: Flask-WTF

### フロントエンド
- **CSS**: Bootstrap 5
- **JavaScript**: Vanilla JS + Chart.js
- **アイコン**: Font Awesome
- **タグ入力**: Tagify

### インフラ・ツール
- **データベース**: PostgreSQL (本番) / SQLite (開発)
- **ホスティング**: Render
- **マイグレーション**: Alembic
- **API連携**: Google Calendar API

## 📸 スクリーンショット

### ログ記録画面
<img src="docs/images/log-form.png" alt="ログ記録画面" width="600">

### ダッシュボード
<img src="docs/images/dashboard.png" alt="ダッシュボード" width="600">

### 統計情報
<img src="docs/images/stats.png" alt="統計情報" width="600">

## 🛠️ セットアップ

### 必要な環境
- Python 3.11以上
- PostgreSQL（本番環境）
- Google Cloud Platform アカウント（カレンダー連携を使用する場合）

### インストール手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/yukita39/learning-log-pwa.git
   cd learning-log-pwa
   ```

2. **仮想環境を作成・有効化**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **依存関係をインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **環境変数を設定**
   ```bash
   # .env ファイルを作成
   cp .env.example .env
   # 必要な値を設定
   ```

5. **データベースを初期化**
   ```bash
   python db.py
   alembic upgrade head
   ```

6. **アプリケーションを起動**
   ```bash
   flask run
   ```

## 🔧 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| SECRET_KEY | Flaskのセッション管理用秘密鍵 | ✅ |
| DATABASE_URL | データベース接続URL | ✅ |
| CALENDAR_ID | デフォルトのGoogle Calendar ID | ❌ |
| SERVICE_CRED | サービスアカウント認証ファイルパス | ❌ |

## 📝 使い方

1. **アカウント登録**: メールアドレスとパスワードで登録
2. **ログイン**: 登録した情報でログイン
3. **学習記録**: フォームから学習内容を入力
4. **タグ追加**: カンマ区切りでタグを追加（例: Python, Flask, Web開発）
5. **統計確認**: ダッシュボードや統計ページで進捗を確認
6. **カレンダー連携**: 設定画面でGoogle Calendar IDを設定（任意）

## 🤝 コントリビューション

プルリクエストを歓迎します！大きな変更の場合は、まずissueを作成して変更内容を議論してください。

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 👤 作者

**yukita39**

- GitHub: [@yukita39](https://github.com/yukita39)

## 🙏 謝辞

- [Flask](https://flask.palletsprojects.com/) - 素晴らしいWebフレームワーク
- [Chart.js](https://www.chartjs.org/) - 美しいグラフライブラリ
- [Bootstrap](https://getbootstrap.com/) - レスポンシブデザイン
- [Render](https://render.com/) - シンプルなホスティングサービス

---

⭐ このプロジェクトが気に入ったら、スターをお願いします！