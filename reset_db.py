# reset_db.py
from db import Base, engine

# 既存テーブルを全て削除
Base.metadata.drop_all(bind=engine)
# 新規にテーブルを作る
Base.metadata.create_all(bind=engine)

print("✅ DB リセット完了")
