import re
from datetime import datetime

def parse_command(text):
    match_all = re.match(r"rappels\s+(\d{2}/\d{2}/\d{4})", text.lower())
    if match_all:
        return {"type": "all", "date": datetime.strptime(match_all.group(1), "%d/%m/%Y")}

    match_one = re.match(r"rappel\s+(.+?)\s+(\d{2}/\d{2}/\d{4})", text.lower())
    if match_one:
        return {
            "type": "single",
            "nom": match_one.group(1).strip().title(),
            "date": datetime.strptime(match_one.group(2), "%d/%m/%Y")
        }

    return {"error": "Commande non reconnue."}
