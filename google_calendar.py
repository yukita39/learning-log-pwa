import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# 環境変数があれば優先。無ければローカル開発用の既定パス
CRED_PATH  = os.getenv("CRED_PATH",  "client_secret.json")
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.json")  # Render では例: /tmp/token.json

print("DEBUG CRED_PATH =", CRED_PATH)
print("DEBUG secrets dir =", os.listdir('/etc/secrets'))

def get_calendar_service():
    creds = None

    # ① 既に token.json があれば読み込む
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # ② 資格情報が無い／期限切れなら更新
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Render のサーバー環境ではブラウザが開けないので
            # ここが呼ばれないように token.json を事前に用意しておくこと
            flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # token.json を保存（サーバーでも /tmp は書き込み可能）
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def add_event(summary, description, start_time, duration_minutes=30):
    service = get_calendar_service()

    event = {
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
    created = service.events().insert(calendarId="primary", body=event).execute()
    return created.get("htmlLink")
