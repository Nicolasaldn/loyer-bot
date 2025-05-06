import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

def get_gsheet_client():
    creds_json = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON"))
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    return gspread.authorize(creds)

def get_sheet_data(sheet_id, tab_name):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id).worksheet(tab_name)
    return sheet.get_all_records()

def get_db_dict(sheet_id, tab_name):
    records = get_sheet_data(sheet_id, tab_name)
    return {r["Nom"]: r["Adresse"] for r in records}
