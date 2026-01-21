import json
import os
from datetime import datetime
from typing import Dict, Any 
from valutatrade_hub.parser_service.config import ParserConfig

class Storage:
    def __init__(self, config: ParserConfig):
        self.config = config
        # Создаем папку data, если её нет
        os.makedirs("data", exist_ok=True)

    def save_rates(self, rates_data: Dict[str, Any]):
        # Определяем путь 
        path = getattr(self.config, "RATES_FILE_PATH", getattr(self.config, "RATES_FILE", "data/rates.json"))
        
        current_data = self._load_json(path, {"pairs": {}})
        
        
        if not isinstance(current_data, dict):
            current_data = {"pairs": {}}
        if "pairs" not in current_data:
            current_data["pairs"] = {}

        for pair, info in rates_data.items():
            current_data["pairs"][pair] = info
        
        current_data["last_refresh"] = datetime.now().isoformat()
        self._atomic_write(path, current_data)

    def save_history(self, rates_data: Dict[str, Any]):
        path = getattr(self.config, "HISTORY_FILE_PATH", "data/exchange_rates.json")
        history = self._load_json(path, [])
        
        if not isinstance(history, list):
            history = []
        
        for pair, info in rates_data.items():
            timestamp = info.get("updated_at", datetime.now().isoformat())
            record = {
                "id": f"{pair}_{timestamp}",
                "pair": pair,
                "rate": info.get("rate"),
                "timestamp": timestamp,
                "source": info.get("source")
            }
            history.append(record)
        
        if len(history) > 500:
            history = history[-500:]
            
        self._atomic_write(path, history)

    def _load_json(self, path: str, default: Any) -> Any:
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default

    def _atomic_write(self, path: str, data: Any):
        temp_path = path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"ERROR: Ошибка записи файла {path}: {e}")