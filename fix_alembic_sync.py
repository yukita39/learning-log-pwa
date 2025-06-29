# fix_alembic_sync.py
from db import engine
from sqlalchemy import text
from alembic.config import Config
from alembic import command

print("=== Alembicとデータベースの同期を修正 ===")

# 1. 現在の状態を確認
with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    current = result.fetchone()
    print(f"現在のAlembicバージョン: {current[0] if current else 'None'}")
    
    # 2. Alembic履歴をクリア
    print("\nAlembic履歴をクリアします...")
    conn.execute(text("DELETE FROM alembic_version"))
    conn.commit()
    print("✅ クリア完了")

# 3. 新しい履歴を作成せずに、現在の状態をマーク
print("\n現在のデータベース状態をAlembicの初期状態としてマークします...")
alembic_cfg = Config("alembic.ini")

# まず空のマイグレーションを作成
print("空の初期マイグレーションを作成...")
try:
    command.revision(alembic_cfg, message="Initial empty migration", autogenerate=False)
    print("✅ 初期マイグレーション作成完了")
except Exception as e:
    print(f"⚠️  マイグレーション作成エラー: {e}")

print("\n次のステップ:")
print("1. 作成されたマイグレーションファイルを確認")
print("2. alembic stamp head を実行")
print("3. 新しい変更用のマイグレーションを作成")