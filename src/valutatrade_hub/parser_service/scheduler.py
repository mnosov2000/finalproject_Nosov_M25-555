import time
import schedule
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.infra.settings import SettingsLoader

def run_scheduler():
    #запуск планировщика
    settings = SettingsLoader()
    ttl = settings.get("RATES_TTL_SECONDS", 300)
    
    updater = RatesUpdater()
    
    print(f"Парсер запущен. Интервал обновления: {ttl} сек.")
    
    print(updater.run())
    
    schedule.every(ttl).seconds.do(lambda: print(updater.run()))
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()