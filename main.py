from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import json

print("📁 Listing des fichiers accessibles")

raw_creds = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")
creds_dict = json.loads(raw_creds)
scopes = ['https://www.googleapis.com/auth/drive.metadata.readonly']
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
service = build('drive', 'v3', credentials=creds)

results = service.files().list(pageSize=50, fields="files(id, name)").execute()
items = results.get('files', [])

if not items:
    print("❌ Aucun fichier accessible.")
else:
    print("📄 Fichiers accessibles :")
    for item in items:
        print(f"- {item['name']} (ID: {item['id']})")
