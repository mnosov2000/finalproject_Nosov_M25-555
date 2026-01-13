from datetime import datetime
from typing import  Dict, Any
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from valutatrade_hub.parser_service.storage import Storage

class RatesUpdater:
    def __init__(self):
        self.config = ParserConfig()
        self.storage = Storage(self.config)
        self.clients = [
            ("CoinGecko", CoinGeckoClient(self.config)),
            ("ExchangeRate-API", ExchangeRateApiClient(self.config))
        ]

    def run_update(self, specific_source: str = None) -> str:
        results: Dict[str, Any] = {}
        errors = []
        now = datetime.now().isoformat()
        total_updated = 0

        print("INFO: Запуск обновления курсов...")

        for name, client in self.clients:
            #фильтр по источнику
            if specific_source and specific_source.lower() not in name.lower():
                continue

            try:
                rates = client.fetch_rates()
                count = len(rates)
                print(f"INFO: Получение данных от {name}... OK ({count} пар)")
                
                for pair, rate in rates.items():
                    results[pair] = {
                        "rate": rate,
                        "updated_at": now,
                        "source": name
                    }
                total_updated += count

            except ApiRequestError as e:
                msg = f"ERROR: Ошибка {name}: {e}"
                print(msg)
                errors.append(msg)
            except Exception as e:
                msg = f"ERROR: Неизвестная ошибка {name}: {e}"
                print(msg)
                errors.append(msg)

        #сохраняем если есть  
        if results:
            print(f"INFO: Сохранение {len(results)} записей в файлы...")
            self.storage.save_rates(results)
            self.storage.save_history(results)
            return f"Успешно обновлено: {total_updated}. Ошибок: {len(errors)}"
        
        if errors:
            raise ApiRequestError(f"Обновление не удалось. Ошибки: {'; '.join(errors)}")
        
        return "Нет данных для обновления."