# ----------  app.py  --------------------------------------------
import csv, os
from datetime import datetime, timedelta
from db import Base, engine
from flask import Flask, render_template, request, jsonify
from sqlalchemy import text
from db import Session, Log
from sqlalchemy import func
from google_calendar import add_event
from collections import Counter

app = Flask(__name__)
CSV_FILE = "log_data.csv"
# ────────────────────────────────────────────────────────────────
# ルート: ホーム（フォーム表示・ログ登録）
# ────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 1) フォーム値
        date_str   = request.form.get("date")
        time_str   = request.form.get("start_time")
        content    = request.form.get("content")
        duration   = int(request.form.get("duration"))
        impression = request.form.get("impression", "")
        tags_raw   = request.form.get("tags", "")            # "Python,Flask"

        date_obj       = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time_obj = datetime.strptime(time_str, "%H:%M").time()
        start_dt       = datetime.combine(date_obj, start_time_obj)
        tag_list       = [t.strip() for t in tags_raw.split(",") if t.strip()]

        # 2) Google カレンダー
        event_link = add_event(
            summary=f"学習：{content}  " + " ".join(f"#{t}" for t in tag_list),
            description=impression,
            start_time=start_dt,
            duration_minutes=duration,
        )

        # 3) DB 保存
        with Session() as s:
            log = Log(
                date=date_obj,
                start_time=start_time_obj,
                duration=duration,
                content=content,
                impression=impression,
                tags=",".join(tag_list),
            )
            s.add(log)
            s.commit()

        # 4) CSV 併存（任意）
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                [date_str, time_str, content, duration, impression, ",".join(tag_list)]
            )

        # 5) 表示
        formatted = f"""👨‍💻 今日のコードログ（#CodeLog）
🧠 やったこと : {content}
🏷 タグ       : {', '.join(tag_list) or 'なし'}
⏱ 時間       : {duration} 分
📅 日付       : {date_str}
📝 メモ       : {impression}
"""

        return render_template("result.html", log=formatted, link=event_link)

    # GET
    return render_template("index.html", today=datetime.today().strftime("%Y-%m-%d"))


# ────────────────────────────────────────────────────────────────
# ルート: 統計（CSV ベースのまま）
# ────────────────────────────────────────────────────────────────
@app.route("/stats")
def stats():
    total_time = 0
    date_set   = set()
    date_list  = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                try:
                    date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
                    date_list.append(date_obj)
                    date_set.add(date_obj)
                    total_time += int(row[3])    # duration 列
                except (ValueError, IndexError):
                    pass

    continued_days = len(date_set)

    # ストリーク計算
    streak = 0
    today  = datetime.today().date()
    for d in sorted(date_list, reverse=True):
        if d == today - timedelta(days=streak):
            streak += 1
        else:
            break

    return render_template(
        "stats.html",
        total_time=total_time,
        days=continued_days,
        streak=streak,
    )


# ────────────────────────────────────────────────────────────────
# ルート: 人気タグ API（Tagify ホワイトリスト用）
# ────────────────────────────────────────────────────────────────
@app.route("/tags/suggest")
def tags_suggest():
    with Session() as s:
        rows = s.query(Log.tags).filter(Log.tags != None).all()   # rows = [( 'Python,Flask' ,)]

    # None・空文字を除外して集計
    words = []
    for (csv_tags,) in rows:
        if not csv_tags:
            continue
        words.extend(t.strip() for t in csv_tags.split(",") if t.strip())

    top20 = [tag for tag, _ in Counter(words).most_common(20)]
    return jsonify(top20)


# ────────────────────────────────────────────────────────────────
# ルート: タグランキング TOP5
# ────────────────────────────────────────────────────────────────
@app.route("/tags/top")
def tags_top():
    with Session() as s:
        rows = s.query(Log.tags).filter(Log.tags != None).all()

    words = []
    for (csv_tags,) in rows:
        if not csv_tags:
            continue
        words.extend(t.strip() for t in csv_tags.split(",") if t.strip())

    top5 = Counter(words).most_common(5)
    return render_template("tags_top.html", rows=top5)


# ────────────────────────────────────────────────────────────────
# ルート: PWA manifest
# ────────────────────────────────────────────────────────────────
@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/stats/data")
def stats_data():
    with Session() as s:
        # 日別累計学習時間
        daily_q = s.query(
            Log.date,
            func.sum(Log.duration).label("total")
        ).group_by(Log.date).order_by(Log.date).all()
        daily = [{"date": d.isoformat(), "duration": total} for d, total in daily_q]

        # タグ使用回数（単純カウント）
        rows = s.query(Log.tags).all()
        c = Counter()
        for (csv_tags,) in rows:
            if csv_tags:
                for tag in csv_tags.split(','):
                    t = tag.strip()
                    if t:
                        c[t] += 1
        tag_share = [{"tag": t, "count": cnt} for t, cnt in c.items()]

    return jsonify({"daily": daily, "tag_share": tag_share})


if __name__ == "__main__":
    app.run(debug=True)
# ----------  app.py  --------------------------------------------
