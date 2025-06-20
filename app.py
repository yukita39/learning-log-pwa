import csv, os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify  # ← jsonify 追加
from google_calendar import add_event
from db import Session, Log                                 # ← SQLAlchemy
from sqlalchemy import text                                 # ランキングSQL用

app = Flask(__name__)
CSV_FILE = "log_data.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # ------------------- フォーム値 -------------------
        date_str   = request.form.get("date")          # 2025-06-21
        time_str   = request.form.get("start_time")    # 09:00
        content    = request.form.get("content")
        duration   = int(request.form.get("duration"))
        impression = request.form.get("impression", "")
        tags_raw   = request.form.get("tags", "")      # "Python,Flask"

        # ---------- Python 型へ変換 & 補助変数 ----------
        date_obj        = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time_obj  = datetime.strptime(time_str, "%H:%M").time()
        start_datetime  = datetime.combine(date_obj, start_time_obj)
        tag_list        = [t.strip() for t in tags_raw.split(",") if t.strip()]

        # ---------------- Google カレンダー --------------
        tag_str = " ".join(f"#{t}" for t in tag_list)   # "#Python #Flask"
        summary  = f"学習：{content}  {tag_str}".strip()
        event_link = add_event(
            summary=summary,
            description=impression,
            start_time=start_datetime,
            duration_minutes=duration    
        )
        print("カレンダーURL:", event_link)

        # ---------------- データベース -------------------
        with Session() as session:
            log = Log(
                date=date_obj,
                start_time=start_time_obj,
                duration=duration,
                content=content,
                impression=impression,
                tags=",".join(tag_list),   # DB は文字列で保持
            )
            session.add(log)
            session.commit()

        # --------------- CSV も併存させる ---------------
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([date_str, time_str, content, duration,
                             impression, ",".join(tag_list)])

        # ---------------- 整形ログ -----------------------
        formatted_log = f"""👨‍💻 今日のコードログ（#CodeLog）

🧠 今日やったこと：
- {content}

🏷 タグ：{', '.join(tag_list) or 'なし'}
⏱ 所要時間：{duration}分
📅 日付：{date_str}
📝 一言メモ：{impression}
"""

        return render_template("result.html", log=formatted_log)

    # —— GET ——
    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("index.html", today=today)

@app.route("/tags/suggest")
def tags_suggest():
    with Session() as s:
        rows = s.execute(text("""
            SELECT TRIM(tag) AS tag, COUNT(*) AS cnt
            FROM logs, json_each('[' || replace(tags, ',', '","') || ']')
            GROUP BY tag
            ORDER BY cnt DESC
            LIMIT 20
        """)).fetchall()
    return jsonify([t for t, _ in rows])

@app.route("/tags/top")
def tags_top():
    with Session() as s:
        rows = s.execute(text("""
            SELECT TRIM(tag) AS tag, COUNT(*) AS cnt
            FROM logs, json_each('[' || replace(tags, ',', '","') || ']')
            GROUP BY tag
            ORDER BY cnt DESC
            LIMIT 5
        """)).fetchall()
    return render_template("tags_top.html", rows=rows)

# /stats ルートはそのまま（CSV 集計）
# manifest ルートもそのまま
if __name__ == "__main__":
    app.run(debug=True)