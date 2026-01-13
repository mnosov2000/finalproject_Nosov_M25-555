import json
import os
from typing import Any, Dict, List

#пути к файлам данных
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PORTFOLIOS_FILE = os.path.join(DATA_DIR, "portfolios.json")
RATES_FILE = os.path.join(DATA_DIR, "rates.json")

def _ensure_file_exists(filepath: str, default_content: Any):
    #создаем файл если его нет
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=4)

def load_json(filepath: str, default: Any) -> Any:
    #читаем джйсон
    _ensure_file_exists(filepath, default)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default

def save_json(filepath: str, data: Any):
    #пишем джйсон
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)