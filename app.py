import csv
import os
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from google_calendar import add_event

app = Flask(__name__)
CSV_FILE = 'log_data.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form.get('date')
        time_str = request.form.get('start_time')
        content = request.form.get('content')
        duration = int(request.form.get('duration'))
        impression = request.form.get('impression')
        
        dt_str = f"{date} {time_str}"
        start_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')

        event_link = add_event(
            summary=f"学習：{content}",
            description=impression,
            start_time=start_time,
            duration_minutes=duration  # 分数
        )
        print("カレンダーに登録されたURL:", event_link)

        formatted_log = f"""\
        
👨‍💻 今日のコードログ（#CodeLog）

🧠 今日やったこと：
- {content}

⏱ 所要時間：{duration}分  
📅 日付：{date}  
📝 一言メモ：{impression}"""
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date, content, duration, impression])

        return render_template('result.html', log=formatted_log)
    else:
        today = datetime.today().strftime('%Y-%m-%d')
        return render_template('index.html', today=today)

@app.route('/stats')
def stats():
    total_time = 0
    date_set = set()
    date_list = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    try:
                        date_obj = datetime.strptime(row[0], '%Y-%m-%d').date()
                        date_list.append(date_obj)
                        date_set.add(date_obj)
                        total_time += int(row[2])
                    except ValueError:
                        pass

    # --- 継続日数 ---
    continued_days = len(date_set)

    # --- 連続記録（ストリーク）計算 ---
    date_list = sorted(set(date_list), reverse=True)
    streak = 0
    today = datetime.today().date()

    for i, d in enumerate(date_list):
        expected_date = today - timedelta(days=streak)
        if d == expected_date:
            streak += 1
        else:
            break

    return render_template('stats.html',
                           total_time=total_time,
                           days=continued_days,
                           streak=streak)

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

if __name__ == '__main__':
    app.run(debug=True)
