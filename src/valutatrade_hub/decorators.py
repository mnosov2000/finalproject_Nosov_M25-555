import functools
import logging
from valutatrade_hub.infra.logging_config import setup_logging

#запускаем логгер
logger = setup_logging()

def log_action(action_name: str = None):
    #декоратор для записи действий
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            #достаем юзера 
            user = getattr(self, 'current_user', None)
            username = user.username if user else "guest"
            
            action = action_name or func.__name__.upper()

            #парсим аргументы
            currency = kwargs.get('currency') or (args[0] if args else '?')
            amount = kwargs.get('amount') or (args[1] if len(args) > 1 else '?')
            
            try:
                result = func(self, *args, **kwargs)
                

                log_msg = (
                    f"{action} user='{username}' "
                    f"currency='{currency}' amount={amount} "
                    f"result=OK"
                )
                logger.info(log_msg)
                return result
                
            except Exception as e:

                error_type = type(e).__name__
                log_msg = (
                    f"{action} user='{username}' "
                    f"currency='{currency}' amount={amount} "
                    f"result=ERROR error_type={error_type} message='{e}'"
                )
                logger.error(log_msg)
                raise e 
                
        return wrapper
    return decorator