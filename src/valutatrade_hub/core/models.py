import hashlib
from datetime import datetime
from typing import Dict, Optional
import copy

class User:
    #класс юзера
    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime
    ):
        #инициализация
        self._user_id = user_id
        #проверка имени через сеттер
        self.username = username 
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым.")
        self._username = value

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self) -> str:
        #инфо о юзере
        return (f"User(ID: {self._user_id}, Name: {self._username}, "
                f"RegDate: {self._registration_date})")

    def change_password(self, new_password: str):
        #смена пароля
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")
        
        #хешируем новый пароль
        self._hashed_password = self._calculate_hash(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        #проверка пароля
        input_hash = self._calculate_hash(password, self._salt)
        return input_hash == self._hashed_password

    @staticmethod
    def _calculate_hash(password: str, salt: str) -> str:
        #хеширование
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def to_dict(self) -> dict:
        #в словарь для джейсона
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }


class Wallet:
    #кошелек для валюты
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом.")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным.")
        self._balance = float(value)

    def deposit(self, amount: float):
        #пополнение
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной.")
        self.balance += amount

    def withdraw(self, amount: float):
        #снятие
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной.")
        if amount > self.balance:
            raise ValueError(f"Недостаточно средств. Текущий баланс: {self.balance}")
        self.balance -= amount

    def get_balance_info(self) -> str:
        #баланс текстом
        return f"{self.balance:.2f} {self.currency_code}"

    def to_dict(self) -> dict:
        #в словарь
        return {
            "currency_code": self.currency_code,
            "balance": self.balance
        }


class Portfolio:
    #портфель с кошельками
    def __init__(self, user_id: int, wallets: Optional[Dict[str, Wallet]] = None):
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = wallets if wallets else {}

    @property
    def user(self) -> int:
        #id юзера
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        #копия кошельков
        return copy.deepcopy(self._wallets)

    def add_currency(self, currency_code: str):
        #добавить валюту если нет
        if currency_code in self._wallets:
            return
        
        self._wallets[currency_code] = Wallet(currency_code=currency_code, balance=0.0)

    def get_wallet(self, currency_code: str) -> Wallet:
        #получить кошелек
        if currency_code not in self._wallets:
            raise ValueError(f"Кошелек для валюты {currency_code} не найден.")
        return self._wallets[currency_code]

    def get_total_value(self, base_currency: str = 'USD', rates: Dict[str, float] = None) -> float:
        #считаем общую стоимость
        if rates is None:
            #заглушка если курсов нет
            rates = {"USD": 1.0, "BTC": 95000.0, "EUR": 1.05}

        total_value = 0.0

        for wallet in self._wallets.values():
            code = wallet.currency_code
            balance = wallet.balance
            
            if code == base_currency:
                total_value += balance
                continue

            rate = rates.get(code, 0.0)
            total_value += balance * rate

        return total_value

    def to_dict(self) -> dict:
        #в словарь
        wallets_data = {
            code: wallet.to_dict() 
            for code, wallet in self._wallets.items()
        }
        return {
            "user_id": self._user_id,
            "wallets": wallets_data
        }