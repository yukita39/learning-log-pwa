"""
Google Calendar 連携  ── サービスアカウント方式専用
・ブラウザ/OAuth フローは完全に除去
・必須ファイルは service_account.json だけ
・書き込み先カレンダーは環境変数 CALENDAR_ID で切替
"""

import os
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

# ─────────────────────────────────────────
SCOPES        = ["https://www.googleapis.com/auth/calendar.events"]
SERVICE_CRED  = os.getenv("SERVICE_CRED", "service_account.json")
CALENDAR_ID   = os.getenv("CALENDAR_ID", "primary")   # 子カレンダーIDを指定可
# ─────────────────────────────────────────

def get_calendar_service_sa():
    """サービスアカウントで Calendar API クライアントを生成"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_CRED, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

def add_event(summary: str,
              description: str,
              start_time: datetime,
              duration_minutes: int = 30) -> str:
    """
    Google カレンダーへ予定を追加し、HTML リンクを返す
      summary           件名
      description       本文
      start_time        開始日時 (datetime tz-naive OK / Asia/Tokyo 固定)
      duration_minutes  所要分数
    """
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

    return created.get("htmlLink")  # 予定詳細ページの URL
