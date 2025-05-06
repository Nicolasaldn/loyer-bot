try:
    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"✅ Fichier ouvert : {spreadsheet.title}")
except Exception as e:
    print(f"❌ Erreur à l'ouverture du fichier : {e}")
