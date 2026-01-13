import json
import os
from typing import Any
from valutatrade_hub.infra.settings import SettingsLoader

#грузим настройки
settings = SettingsLoader()

#пути берем из конфига
USERS_FILE = settings.get("USERS_FILE")
PORTFOLIOS_FILE = settings.get("PORTFOLIOS_FILE")
RATES_FILE = settings.get("RATES_FILE")

def _ensure_file_exists(filepath: str, default_content: Any):
    #создаем папку если её нет
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=4)

def load_json(filepath: str, default: Any) -> Any:
    #читаем файл
    _ensure_file_exists(filepath, default)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default

def save_json(filepath: str, data: Any):
    #пишем файл
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)