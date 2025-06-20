import csv, os
from datetime import datetime, timedelta
from flask import Flask, render_template, request
from google_calendar import add_event
from db import Session, Log                 # ← SQLAlchemy

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
        event_link = add_event(
            summary=f"学習：{content}",
            description=impression,
            start_time=start_datetime,
            duration_minutes=duration,
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


# /stats ルートはそのまま（CSV 集計）
# manifest ルートもそのまま
if __name__ == "__main__":
    app.run(debug=True)