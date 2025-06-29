📋 Working Log PWA - 作業記録管理アプリケーション

作業の進捗を記録し、Google カレンダーと連携できる Progressive Web App (PWA) です。
日々の作業を可視化し、生産性の向上をサポートします。
🌟 主な機能
📝 作業ログ管理

簡単記録: 日付、時間、内容、感想をフォームから簡単入力
タグ機能: 作業内容をタグで分類・整理
よく使うタグ: 頻繁に使用するタグをワンクリックで追加

📊 統計・可視化

作業統計: 総作業時間、継続日数、連続記録日数を表示
ダッシュボード: Chart.jsを使用した美しいグラフで進捗を可視化

日別・週別・月別の作業時間推移
タグ別の作業時間分布


タグランキング: よく使うタグTOP5を表示

📅 Google カレンダー連携

自動記録: 作業ログを自動的にGoogleカレンダーに追加
プライバシー重視: ユーザーが明示的に設定した場合のみ連携
柔軟な設定: 個人のカレンダーIDを設定可能

🔐 セキュリティ

ユーザー認証: Flask-Loginによる安全な認証システム
パスワード保護: Werkzeugによるハッシュ化
セッション管理: HTTPOnly、Secure、SameSiteクッキー設定

📱 PWA対応

オフライン対応: Service Workerによるキャッシュ機能
インストール可能: デスクトップ・モバイルにアプリとしてインストール
レスポンシブデザイン: Bootstrap 5による美しいUI

🚀 技術スタック
バックエンド

言語: Python 3.11
フレームワーク: Flask 2.3.3
ORM: SQLAlchemy 1.4
認証: Flask-Login
フォーム: Flask-WTF

フロントエンド

CSS: Bootstrap 5
JavaScript: Vanilla JS + Chart.js
アイコン: Font Awesome
タグ入力: Tagify

インフラ・ツール

データベース: PostgreSQL (本番) / SQLite (開発)
ホスティング: Render
マイグレーション: Alembic
API連携: Google Calendar API

📸 スクリーンショット
ログ記録画面
<img src="docs/images/log-form.png" alt="ログ記録画面" width="600">
ダッシュボード
<img src="docs/images/dashboard.png" alt="ダッシュボード" width="600">
統計情報
<img src="docs/images/stats.png" alt="統計情報" width="600">
🛠️ セットアップ
必要な環境

Python 3.11以上
PostgreSQL（本番環境）
Google Cloud Platform アカウント（カレンダー連携を使用する場合）

インストール手順

リポジトリをクローン
bashgit clone https://github.com/yukita39/learning-log-pwa.git
cd learning-log-pwa

仮想環境を作成・有効化
bashpython -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

依存関係をインストール
bashpip install -r requirements.txt

環境変数を設定
bash# .env ファイルを作成
cp .env.example .env
# 必要な値を設定

データベースを初期化
bashpython db.py
alembic upgrade head

アプリケーションを起動
bashflask run


🔧 環境変数
変数名説明必須SECRET_KEYFlaskのセッション管理用秘密鍵✅DATABASE_URLデータベース接続URL✅CALENDAR_IDデフォルトのGoogle Calendar ID❌SERVICE_CREDサービスアカウント認証ファイルパス❌
📝 使い方

アカウント登録: メールアドレスとパスワードで登録
ログイン: 登録した情報でログイン
作業記録: フォームから作業内容を入力
タグ追加: カンマ区切りでタグを追加（例: 開発, ミーティング, ドキュメント作成）
統計確認: ダッシュボードや統計ページで進捗を確認
カレンダー連携: 設定画面でGoogle Calendar IDを設定（任意）

🤝 コントリビューション
プルリクエストを歓迎します！大きな変更の場合は、まずissueを作成して変更内容を議論してください。

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request

📄 ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
👤 作者
yukita39

GitHub: @yukita39

🙏 謝辞

Flask - 素晴らしいWebフレームワーク
Chart.js - 美しいグラフライブラリ
Bootstrap - レスポンシブデザイン
Render - シンプルなホスティングサービス


⭐ このプロジェクトが気に入ったら、スターをお願いしま