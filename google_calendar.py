"""
Google Calendar 連携  ── サービスアカウント方式専用
・ブラウザ/OAuth フローは完全に除去
・必須ファイルは service_account.json だけ
・書き込み先カレンダーは環境変数 CALENDAR_ID で切替
"""

import os
from datetime import datetime, timedelta, date, time

from google.oauth2 import service_account
from googleapiclient.discovery import build

# ─────────────────────────────────────────
SCOPES        = ["https://www.googleapis.com/auth/calendar.events"]
SERVICE_CRED  = os.getenv("SERVICE_CRED", "service_account.json")
CALENDAR_ID   = os.getenv("CALENDAR_ID", "primary")   # 子カレンダーIDを指定可
# ─────────────────────────────────────────

def get_calendar_service_sa():
    """サービスアカウントで Calendar API クライアントを生成"""
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_CRED, scopes=SCOPES
        )
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        print(f"サービスアカウント認証エラー: {e}")
        raise

def add_event(calendar_id, date_obj, time_obj, duration_minutes, content, impression=None, tags=None):
    """
    Google カレンダーへ予定を追加（app.py からの呼び出しに対応）
    
    Args:
        calendar_id: カレンダーID（使用する場合）
        date_obj: 日付オブジェクト (date)
        time_obj: 時刻オブジェクト (time)
        duration_minutes: 所要時間（分）
        content: 作業内容（カレンダーのタイトルになる）
        impression: 感想・メモ（オプション）
        tags: タグ（オプション）
    
    Returns:
        str: 作成されたイベントのHTMLリンク、または None
    """
    try:
        # date と time を datetime に結合
        start_datetime = datetime.combine(date_obj, time_obj)
        
        # サービスを取得
        service = get_calendar_service_sa()
        
        # カレンダーIDの決定（引数で渡されたものを優先、なければ環境変数）
        target_calendar_id = calendar_id if calendar_id != "primary" else CALENDAR_ID
        
        # タイトルの作成（タグを含む）
        title = f"📚 {content}"
        if tags and tags.strip():
            # タグをハッシュタグ形式で追加
            tag_list = [f"#{tag.strip()}" for tag in tags.split(',') if tag.strip()]
            title += f" {' '.join(tag_list)}"
        
        # 説明文の作成（感想・メモを含む）
        description_parts = [
            f"作業内容: {content}",
            f"記録時間: {duration_minutes}分"
        ]
        
        if impression and impression.strip():
            description_parts.append(f"\n感想・メモ:\n{impression}")
        
        if tags and tags.strip():
            description_parts.append(f"\nタグ: {tags}")
        
        description = "\n".join(description_parts)
        
        # イベントの作成
        event_body = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": "Asia/Tokyo",
            },
            "end": {
                "dateTime": (start_datetime + timedelta(minutes=duration_minutes)).isoformat(),
                "timeZone": "Asia/Tokyo",
            },
        }
        
        print(f"カレンダーにイベントを追加: {event_body['summary']}")
        
        created = service.events().insert(
            calendarId=target_calendar_id,
            body=event_body
        ).execute()
        
        html_link = created.get("htmlLink")
        print(f"カレンダーイベント作成成功: {html_link}")
        
        return html_link
        
    except FileNotFoundError as e:
        print(f"認証ファイルが見つかりません: {SERVICE_CRED}")
        print(f"エラー詳細: {e}")
        return None
    except Exception as e:
        print(f"カレンダーイベント作成エラー: {type(e).__name__}: {e}")
        return None


# 既存の関数も残す（他の場所で使われている場合のため）
def add_event_with_details(summary: str,
                          description: str,
                          start_time: datetime,
                          duration_minutes: int = 30) -> str:
    """
    詳細指定版（元の関数）
    """
    try:
        service = get_calendar_service_sa()

        event_body = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Tokyo",
            },
            "end": {
                "dateTime": (start_time + timedelta(minutes=duration_minutes)).isoformat(),
                "timeZone": "Asia/Tokyo",
            },
        }

        created = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event_body
        ).execute()

        return created.get("htmlLink")
    except Exception as e:
        print(f"カレンダーイベント作成エラー: {e}")
        return None