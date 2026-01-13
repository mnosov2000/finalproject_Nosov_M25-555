import json
import os
from datetime import datetime
from typing import Dict, Any 
from valutatrade_hub.parser_service.config import ParserConfig

class Storage:
    def __init__(self, config: ParserConfig):
        self.config = config

    def save_rates(self, rates_data: Dict[str, Any]):
        # пишем актуальные курсы
        current_data = self._load_json(self.config.RATES_FILE_PATH, {"pairs": {}})
        
        for pair, info in rates_data.items():
            current_data["pairs"][pair] = info
        
        current_data["last_refresh"] = datetime.now().isoformat()
        
        self._atomic_write(self.config.RATES_FILE_PATH, current_data)

    def save_history(self, rates_data: Dict[str, Any]):
        # пишем историю
        history = self._load_json(self.config.HISTORY_FILE_PATH, [])
        
        for pair, info in rates_data.items():
            timestamp = info["updated_at"]
            record_id = f"{pair}_{timestamp}"
            
            record = {
                "id": record_id,
                "pair": pair,
                "rate": info["rate"],
                "timestamp": timestamp,
                "source": info["source"]
            }
            history.append(record)
        
        # храним последние 500 записей
        if len(history) > 500:
            history = history[-500:]
            
        self._atomic_write(self.config.HISTORY_FILE_PATH, history)

    def _load_json(self, path: str, default: Any) -> Any:
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default

    def _atomic_write(self, path: str, data: Any):
        #пишем безопасно через tmp файл
        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)