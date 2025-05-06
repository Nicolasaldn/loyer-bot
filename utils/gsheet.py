import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_worksheets():
    raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")
    creds_dict = json.loads(raw_creds)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("RE - Gestion")
    return spreadsheet.worksheet("Interface"), spreadsheet.worksheet("DB")
