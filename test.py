import json
from pathlib import Path

if (p:=Path("storage/data.json")).exists():
    with open(p, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}
else:
    with open(p, 'w', encoding='utf-8') as file:
        json.dump({}, file, ensure_ascii=False, indent=4)