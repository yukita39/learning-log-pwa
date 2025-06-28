# app.py
import os
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
import json

# db.py からインポート
from db import Session, Log, User, Base, engine
from google_calendar import add_event

# forms.py が存在する場合はインポート（後で作成予定）
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# Flask-Login設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'このページにアクセスするにはログインが必要です'

def get_service_credentials():
    # 環境変数から読み込む
    cred_json = os.getenv('SERVICE_CRED_JSON')
    if cred_json:
        return json.loads(cred_json)
    # ローカルファイルから読み込む
    else:
        with open('service_account.json', 'r') as f:
            return json.load(f)

@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        return session.query(User).get(int(user_id))

# --- ルート: ユーザー登録 ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        with Session() as session:
            new_user = User(
                email=form.email.data,
                username=form.username.data
            )
            new_user.set_password(form.password.data)
            
            session.add(new_user)
            session.commit()
            
            flash("登録が完了しました！ログインしてください。", "success")
            return redirect(url_for("login"))
    
    return render_template("register.html", form=form)

# --- ルート: ログイン ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        with Session() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('メールアドレスまたはパスワードが正しくありません', 'danger')
    
    return render_template('login.html', form=form)

# --- ルート: ログアウト ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')  # リダイレクトではなくテンプレート表示

# --- 既存: フォーム表示 （ログイン必須） ---
@app.route('/')
@login_required
def index():
    return render_template('index.html', today=datetime.today().strftime('%Y-%m-%d'))

# ログ記録処理（POSTのみ） - 1つだけ残す
@app.route('/log', methods=['POST'])
@login_required
def log():
    try:
        # フォームからデータ取得
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        duration = int(request.form.get('duration', 0))
        content = request.form.get('content', '')
        impression = request.form.get('impression', '')
        tags = request.form.get('tags', '')
        
        # 日付と時刻の変換
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        
        # セッションを使用してログを保存
        session = Session()
        try:
            new_log = Log(
                date=date_obj,
                start_time=time_obj,
                duration=duration,
                content=content,
                impression=impression,
                tags=tags,
                user_id=current_user.id
            )
            session.add(new_log)
            session.commit()
            
            # Google Calendar に追加
            calendar_success = False
            calendar_error = None
            
            try:
                # 現在のユーザーのカレンダーIDを取得
                user = session.query(User).get(current_user.id)
                calendar_id = user.calendar_id if user.calendar_id else os.getenv("CALENDAR_ID", "primary")
                
                print(f"使用するカレンダーID: {calendar_id}")
                
                # add_event 関数を呼び出し（タグと感想も渡す）
                result = add_event(
                    calendar_id, 
                    date_obj, 
                    time_obj, 
                    duration, 
                    content,
                    impression,  # 感想・メモを追加
                    tags         # タグを追加
                )
                
                if result:
                    calendar_success = True
                    print("Google Calendar への追加成功")
                else:
                    print("Google Calendar への追加に失敗")
                    
            except ImportError as e:
                calendar_error = f"Google Calendar モジュールのインポートエラー: {e}"
                print(calendar_error)
            except FileNotFoundError as e:
                calendar_error = f"認証ファイルが見つかりません: {e}"
                print(calendar_error)
            except Exception as e:
                calendar_error = f"Google Calendar エラー: {type(e).__name__}: {e}"
                print(calendar_error)
            
            # メッセージ表示
            if calendar_success:
                flash('ログを記録し、カレンダーに追加しました', 'success')
            else:
                if calendar_error:
                    flash(f'ログは記録されました（カレンダー追加失敗: {calendar_error}）', 'warning')
                else:
                    flash('ログは記録されました（カレンダーには追加されませんでした）', 'warning')
            
        finally:
            session.close()
        
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"ログ登録エラー: {e}")
        flash(f'ログの登録に失敗しました: {str(e)}', 'danger')
        return redirect(url_for('index'))

# ログ一覧表示
@app.route('/logs')
@login_required
def logs():
    session = Session()
    try:
        # 現在のユーザーのログのみ取得（新しい順）
        user_logs = session.query(Log).filter_by(user_id=current_user.id).order_by(Log.date.desc(), Log.start_time.desc()).all()
        return render_template('logs.html', logs=user_logs)
    finally:
        session.close()

# --- 統計表示 ---
@app.route('/stats')
@login_required
def stats():
    session = Session()
    try:
        # 現在のユーザーのログのみで統計を計算
        user_logs = session.query(Log).filter_by(user_id=current_user.id).order_by(Log.date.desc()).all()
        
        if not user_logs:
            return render_template('stats.html', 
                                 days=0,
                                 streak=0,
                                 total_time=0,
                                 logs=[])
        
        # 統計計算
        total_time = sum(log.duration for log in user_logs)  # total_time に変更
        days = len(set(log.date for log in user_logs))  # days に変更
        
        # 連続日数の計算
        dates = sorted(set(log.date for log in user_logs))
        streak = 1
        current_streak = 1
        
        # 今日から逆算して連続日数を計算
        today = date.today()
        if dates and dates[-1] == today:
            # 今日の記録がある場合
            for i in range(len(dates) - 1, 0, -1):
                if (dates[i] - dates[i-1]).days == 1:
                    current_streak += 1
                else:
                    break
            streak = current_streak
        elif dates and (today - dates[-1]).days == 1:
            # 昨日の記録がある場合
            for i in range(len(dates) - 1, 0, -1):
                if (dates[i] - dates[i-1]).days == 1:
                    current_streak += 1
                else:
                    break
            streak = current_streak
        else:
            # 連続が途切れている
            streak = 0
        
        return render_template('stats.html', 
                             days=days,  # 継続日数
                             streak=streak,  # 連続記録日数
                             total_time=total_time,  # 累計学習時間
                             logs=user_logs)  # ログリスト（追加情報用）
    finally:
        session.close()

# ダッシュボード
@app.route('/dashboard')
@login_required
def dashboard():
    # ダッシュボード用のデータを取得する処理
    return render_template('dashboard.html')

# --- タグランキング表示（修正版） ---
@app.route('/tags_top')
@app.route('/tags/top')  # 既存のリンクに対応
@login_required
def tags_top():
    session = Session()
    try:
        # 現在のユーザーのログを取得
        user_logs = session.query(Log).filter_by(user_id=current_user.id).all()
        
        # タグをカウント
        tag_count = defaultdict(int)
        for log in user_logs:
            if log.tags:
                # カンマで分割してタグを抽出
                tags = [tag.strip() for tag in log.tags.split(',') if tag.strip()]
                for tag in tags:
                    tag_count[tag] += 1
        
        # 上位5件を取得
        rows = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return render_template('tags_top.html', rows=rows)
    finally:
        session.close()

# ダッシュボード用のAPIエンドポイント（dashboard.jsから呼ばれる）
@app.route('/api/dashboard')
@login_required
def api_dashboard():
    session = Session()
    try:
        # キャッシュ用の基本データ構造
        result_data = {
            'daily': {'labels': [], 'data': []},
            'tags': {'labels': [], 'data': []},
            'weekly': {'labels': [], 'data': []},
            'monthly': {'labels': [], 'data': []},
            'stats': {
                'total_hours': 0,
                'total_logs': 0,
                'avg_duration': 0,
                'total_tags': 0
            }
        }
        
        # 現在のユーザーのログを取得（必要なフィールドのみ）
        user_logs = session.query(
            Log.date, 
            Log.duration, 
            Log.tags
        ).filter_by(
            user_id=current_user.id
        ).order_by(Log.date).all()
        
        if not user_logs:
            return jsonify(result_data)
        
        # 高速化のため、一度のループで全データを集計
        daily_data = defaultdict(int)
        tag_data = defaultdict(int)
        weekly_data = defaultdict(int)
        monthly_data = defaultdict(int)
        total_duration = 0
        
        for log in user_logs:
            total_duration += log.duration
            
            # 日別集計
            date_str = log.date.strftime('%Y-%m-%d')
            daily_data[date_str] += log.duration
            
            # 週別集計
            week_start = log.date - timedelta(days=log.date.weekday())
            week_str = week_start.strftime('%Y-%m-%d')
            weekly_data[week_str] += log.duration
            
            # 月別集計
            month_str = log.date.strftime('%Y-%m')
            monthly_data[month_str] += log.duration
            
            # タグ集計（タグがある場合のみ）
            if log.tags:
                for tag in log.tags.split(','):
                    tag = tag.strip()
                    if tag:
                        tag_data[tag] += log.duration
        
        # 統計情報
        total_logs = len(user_logs)
        avg_duration = total_duration / total_logs if total_logs > 0 else 0
        
        # 日別データ（最近30日分のみ）
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            result_data['daily']['labels'].append(current_date.strftime('%m/%d'))
            result_data['daily']['data'].append(daily_data.get(date_str, 0))
        
        # タグデータ（上位5件のみ）
        if tag_data:
            sorted_tags = sorted(tag_data.items(), key=lambda x: x[1], reverse=True)[:5]
            result_data['tags']['labels'] = [tag for tag, _ in sorted_tags]
            result_data['tags']['data'] = [duration for _, duration in sorted_tags]
        
        # 週別データ（最近8週分のみ）
        if weekly_data:
            weekly_sorted = sorted(weekly_data.items())[-8:]
            result_data['weekly']['labels'] = [
                datetime.strptime(week, '%Y-%m-%d').strftime('%m/%d') 
                for week, _ in weekly_sorted
            ]
            result_data['weekly']['data'] = [duration for _, duration in weekly_sorted]
        
        # 月別データ（最近6ヶ月分のみ）
        if monthly_data:
            monthly_sorted = sorted(monthly_data.items())[-6:]
            result_data['monthly']['labels'] = [
                datetime.strptime(month, '%Y-%m').strftime('%Y/%m') 
                for month, _ in monthly_sorted
            ]
            result_data['monthly']['data'] = [duration for _, duration in monthly_sorted]
        
        # 統計情報を更新
        result_data['stats'] = {
            'total_hours': round(total_duration / 60, 1),
            'total_logs': total_logs,
            'avg_duration': round(avg_duration, 1),
            'total_tags': len(tag_data)
        }
        
        return jsonify(result_data)
        
    finally:
        session.close()

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """ユーザー設定ページ"""
    session = Session()
    try:
        user = session.query(User).get(current_user.id)
        
        if request.method == 'POST':
            # カレンダーIDの更新
            calendar_id = request.form.get('calendar_id', '').strip()
            
            if calendar_id:
                user.calendar_id = calendar_id
                session.commit()
                flash('カレンダーIDを更新しました', 'success')
            else:
                user.calendar_id = None
                session.commit()
                flash('カレンダーIDをデフォルトに戻しました', 'info')
            
            return redirect(url_for('settings'))
        
        # 現在の設定を表示
        current_calendar_id = user.calendar_id or os.getenv("CALENDAR_ID", "primary")
        return render_template('settings.html', current_calendar_id=current_calendar_id)
        
    finally:
        session.close()

@app.route('/api/popular-tags')
@login_required
def popular_tags():
    """よく使うタグを取得するAPI"""
    session = Session()
    try:
        # 現在のユーザーのログからタグを集計
        user_logs = session.query(Log).filter_by(user_id=current_user.id).all()
        
        # タグの使用回数をカウント
        tag_count = defaultdict(int)
        for log in user_logs:
            if log.tags:
                # カンマで分割してタグを抽出
                tags = [tag.strip() for tag in log.tags.split(',') if tag.strip()]
                for tag in tags:
                    tag_count[tag] += 1
        
        # 使用回数の多い順にソート（上位10件）
        popular_tags_list = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # タグ名のリストとして返す
        result = [{'tag': tag, 'count': count} for tag, count in popular_tags_list]
        
        return jsonify(result)
        
    finally:
        session.close()

# result ページ（オプション）
@app.route('/result')
@login_required
def result():
    # 最新のログを整形して表示
    session = Session()
    try:
        latest_log = session.query(Log).filter_by(user_id=current_user.id).order_by(Log.date.desc(), Log.start_time.desc()).first()
        
        if latest_log:
            # ログを整形
            log_text = f"""日付: {latest_log.date.strftime('%Y年%m月%d日')}
開始時刻: {latest_log.start_time.strftime('%H:%M')}
学習時間: {latest_log.duration}分
学習内容: {latest_log.content}
感想: {latest_log.impression or 'なし'}
タグ: {latest_log.tags or 'なし'}"""
        else:
            log_text = "ログがありません"
        
        return render_template('result.html', log=log_text)
    finally:
        session.close()

if __name__ == '__main__':
    # テーブルが存在しない場合は作成
    Base.metadata.create_all(engine)
    app.run(debug=True)