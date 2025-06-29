# simple_db_check.py
import os
from dotenv import load_dotenv
from sqlalchemy import text, inspect

# .envファイルを読み込み
load_dotenv()

print("=== 環境確認 ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

# データベース接続
from db import engine, DATABASE_URL

print(f"\n=== データベース情報 ===")
print(f"接続先: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

try:
    # インスペクターを使用してテーブル情報を取得
    inspector = inspect(engine)
    
    # テーブル一覧
    tables = inspector.get_table_names()
    print(f"\n既存のテーブル: {tables}")
    
    # 各テーブルのカラム情報
    for table in tables:
        print(f"\n{table} テーブルのカラム:")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    # alembic_versionテーブルの確認
    if 'alembic_version' in tables:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                print(f"\n現在のAlembicバージョン: {version[0]}")
    
    print("\n✅ データベース接続成功！PostgreSQLを使用しています。")
    
except Exception as e:
    print(f"\n❌ エラー: {e}")
    print("エラーの詳細:", type(e).__name__)