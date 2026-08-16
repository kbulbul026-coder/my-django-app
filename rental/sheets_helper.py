import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings
from django.utils import timezone


def get_sheet():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(
        settings.GOOGLE_SHEETS_CREDENTIALS,
        scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1
    return sheet


def log_to_sheet(action, tenant_name="", details="", amount="", month=""):
    try:
        sheet = get_sheet()
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            timestamp,
            action,
            tenant_name,
            details,
            str(amount),
            month
        ]
        sheet.append_row(row)
        print("Logged to Google Sheets successfully")
        return True
    except Exception as e:
        print("Google Sheets Error:", e)
        return False
