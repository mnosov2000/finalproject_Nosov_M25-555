import logging
from logging.handlers import RotatingFileHandler
from valutatrade_hub.infra.settings import SettingsLoader

def setup_logging():
    #настройка логгера
    settings = SettingsLoader()
    
    log_file = settings.get("LOG_FILE")
    log_level = settings.get("LOG_LEVEL")
    log_format = settings.get("LOG_FORMAT")

    logger = logging.getLogger("valutatrade_hub")
    logger.setLevel(log_level)

    #чистим старые хендлеры
    if logger.handlers:
        logger.handlers.clear()

    #ротация файлов  
    handler = RotatingFileHandler(
        log_file, 
        maxBytes=1_000_000, 
        backupCount=3, 
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    return logger