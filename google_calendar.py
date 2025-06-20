import os, shutil
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CRED_PATH  = os.getenv("CRED_PATH",  "client_secret.json")
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.json")
SERVICE_CRED = os.getenv("SERVICE_CRED", "service_account.json")
CALENDAR_ID  = os.getenv("CALENDAR_ID", "primary") 

# --- SecretFile は read-only なので /tmp にコピーして編集可にする ---
TMP_TOKEN = "/tmp/token.json"
if os.path.exists(TOKEN_PATH) and not os.path.exists(TMP_TOKEN):
    shutil.copy(TOKEN_PATH, TMP_TOKEN)          # 1 回だけコピー
TOKEN_PATH = TMP_TOKEN                          # 以降は /tmp を使用

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # サーバー環境では認証フローを走らせない
            raise RuntimeError("token.json が無効です。再生成してください。")

        # /tmp は書き込み可
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def add_event(summary, description, start_time, duration_minutes=30):
    service = get_calendar_service_sa() 

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
    created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created.get("htmlLink")

def get_calendar_service_sa():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_CRED, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds)