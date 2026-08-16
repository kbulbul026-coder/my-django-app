import time
import threading
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


def _log_to_sheet_sync(action, tenant_name="", room="", bill_month="", amount="", 
                       payment_method="", note="", status="Success"):
    """Actual logging function (runs in background)"""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            sheet = get_sheet()
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

            row = [
                timestamp,
                action,
                tenant_name,
                room,
                bill_month,
                str(amount),
                payment_method,
                note,
                status
            ]
            sheet.append_row(row)
            print("Logged to Google Sheets successfully")
            return True

        except Exception as e:
            print(f"Google Sheets Error (attempt {attempt+1}):", e)
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("Failed to log after 3 attempts")
                return False


def log_to_sheet(action, tenant_name="", room="", bill_month="", amount="", 
                 payment_method="", note="", status="Success"):
    """
    Asynchronous version - does not block the main request
    """
    thread = threading.Thread(
        target=_log_to_sheet_sync,
        args=(action, tenant_name, room, bill_month, amount, payment_method, note, status)
    )
    thread.daemon = True   # dies when main program exits
    thread.start()
