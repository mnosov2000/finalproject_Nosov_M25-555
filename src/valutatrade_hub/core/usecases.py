import secrets
from datetime import datetime, timedelta
from typing import Optional

from valutatrade_hub.core.models import User, Portfolio, Wallet
from valutatrade_hub.core.utils import (
    load_json, save_json, USERS_FILE, PORTFOLIOS_FILE, RATES_FILE
)
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError, CurrencyNotFoundError, ApiRequestError
)
from valutatrade_hub.decorators import log_action
from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.infra.settings import SettingsLoader

MOCK_RATES = {
    "BTC_USD": 59337.21,
    "ETH_USD": 3720.00,
    "EUR_USD": 1.0786,
    "RUB_USD": 0.01016
}

class CoreService:
    def __init__(self):
        self.current_user: Optional[User] = None
        self.settings = SettingsLoader()

    @log_action(action_name="REGISTER")
    def register(self, username: str, password: str) -> str:
        users_data = load_json(USERS_FILE, [])
        
        for u in users_data:
            if u["username"] == username:
                raise ValueError(f"Имя пользователя '{username}' уже занято")

        user_id = len(users_data) + 1
        salt = secrets.token_hex(8)
        
        temp_user = User(user_id, username, "", salt, datetime.now())
        temp_user.change_password(password)

        users_data.append(temp_user.to_dict())
        save_json(USERS_FILE, users_data)

        #создаем кошелек и даем бонус
        portfolios = load_json(PORTFOLIOS_FILE, [])
        new_portfolio_data = {
            "user_id": user_id, 
            "wallets": {
                "USD": {"currency_code": "USD", "balance": 1000.0}
            }
        }
        portfolios.append(new_portfolio_data)
        save_json(PORTFOLIOS_FILE, portfolios)

        return f"Пользователь '{username}' зарегистрирован (id={user_id}). Вам начислен стартовый бонус 1000.00 USD!"

    @log_action(action_name="LOGIN")
    def login(self, username: str, password: str) -> str:
        users_data = load_json(USERS_FILE, [])
        found_user_data = next((u for u in users_data if u["username"] == username), None)

        if not found_user_data:
            raise ValueError(f"Пользователь '{username}' не найден")

        user = User(
            user_id=found_user_data["user_id"],
            username=found_user_data["username"],
            hashed_password=found_user_data["hashed_password"],
            salt=found_user_data["salt"],
            registration_date=datetime.fromisoformat(found_user_data["registration_date"])
        )

        if user.verify_password(password):
            self.current_user = user
            return f"Вы вошли как '{username}'"
        else:
            raise ValueError("Неверный пароль")

    def _get_portfolio(self) -> Portfolio:
        if not self.current_user:
            raise ValueError("Сначала выполните login")
            
        portfolios_data = load_json(PORTFOLIOS_FILE, [])
        user_p_data = next((p for p in portfolios_data if p["user_id"] == self.current_user.user_id), None)
        
        if not user_p_data:
            p = Portfolio(self.current_user.user_id)
            p.add_currency("USD")
            return p
            
        wallets = {}
        for code, w_data in user_p_data.get("wallets", {}).items():
            wallets[code] = Wallet(code, w_data["balance"])
            
        return Portfolio(self.current_user.user_id, wallets)

    def _save_portfolio(self, portfolio: Portfolio):
        all_data = load_json(PORTFOLIOS_FILE, [])
        all_data = [p for p in all_data if p["user_id"] != portfolio.user]
        all_data.append(portfolio.to_dict())
        save_json(PORTFOLIOS_FILE, all_data)

    def show_portfolio(self, base_currency: str = "USD") -> str:
        get_currency(base_currency)

        portfolio = self._get_portfolio()
        wallets = portfolio.wallets
        
        if not wallets:
            return "У вас пока нет кошельков."

        rates_data = self._load_rates()
        output = [f"Портфель пользователя '{self.current_user.username}' (база: {base_currency}):"]
        
        total = 0.0
        sorted_codes = sorted(wallets.keys(), key=lambda x: (x != "USD", x))
        
        for code in sorted_codes:
            wallet = wallets[code]
            try:
                curr_obj = get_currency(code)
                display_name = curr_obj.name
            except CurrencyNotFoundError:
                display_name = code

            rate = self._get_rate_value(code, base_currency, rates_data)
            value = wallet.balance * rate
            total += value
            output.append(f"- {code} ({display_name}): {wallet.balance:.4f}  → {value:.2f} {base_currency}")
            
        output.append("-" * 33)
        output.append(f"ИТОГО: {total:.2f} {base_currency}")
        return "\n".join(output)

    @log_action(action_name="BUY")
    def buy(self, currency: str, amount: float) -> str:
        if amount <= 0:
            raise ValueError("'amount' должен быть положительным числом")
        if currency == "USD":
            raise ValueError("Нельзя купить USD за USD.")
        
        get_currency(currency)
            
        portfolio = self._get_portfolio()
        
        try:
            usd_wallet = portfolio.get_wallet("USD")
        except ValueError:
            portfolio.add_currency("USD")
            usd_wallet = portfolio.get_wallet("USD")
            
        rates = self._load_rates()
        # ВОТ ЗДЕСЬ РАНЬШЕ БЫЛА ОШИБКА, ТЕПЕРЬ МЕТОД ЕСТЬ ВНИЗУ
        rate_to_usd = self._get_rate_value(currency, "USD", rates)
        if rate_to_usd == 0:
             raise ApiRequestError(f"Нет курса для {currency}")
             
        cost_in_usd = amount * rate_to_usd
        
        if usd_wallet.balance < cost_in_usd:
            raise InsufficientFundsError(usd_wallet.balance, cost_in_usd, "USD")
            
        usd_wallet.withdraw(cost_in_usd)
        
        portfolio.add_currency(currency)
        target_wallet = portfolio.get_wallet(currency)
        target_wallet.deposit(amount)
        
        self._save_portfolio(portfolio)
        
        return (f"Покупка выполнена: {amount:.4f} {currency} за {cost_in_usd:.2f} USD\n"
                f"Баланс USD: {usd_wallet.balance:.2f}")

    @log_action(action_name="SELL")
    def sell(self, currency: str, amount: float) -> str:
        if amount <= 0:
            raise ValueError("'amount' должен быть положительным числом")
        if currency == "USD":
            raise ValueError("Нельзя продать USD.")

        get_currency(currency)
            
        portfolio = self._get_portfolio()
        
        try:
            target_wallet = portfolio.get_wallet(currency)
        except ValueError:
            raise ValueError(f"У вас нет кошелька '{currency}'.")

        target_wallet.withdraw(amount)
        
        rates = self._load_rates()
        rate_to_usd = self._get_rate_value(currency, "USD", rates)
        revenue_in_usd = amount * rate_to_usd
        
        try:
            usd_wallet = portfolio.get_wallet("USD")
        except ValueError:
            portfolio.add_currency("USD")
            usd_wallet = portfolio.get_wallet("USD")
            
        usd_wallet.deposit(revenue_in_usd)
        self._save_portfolio(portfolio)
        
        return (f"Продажа выполнена: {amount:.4f} {currency} за {revenue_in_usd:.2f} USD\n"
                f"Баланс USD: {usd_wallet.balance:.2f}")

    def get_rate(self, from_currency: str, to_currency: str) -> str:
        get_currency(from_currency)
        get_currency(to_currency)

        rates = self._load_rates()
        self._check_rates_freshness(rates)
        
        rate = self._get_rate_value(from_currency, to_currency, rates)
        
        updated = "N/A"
        direct = f"{from_currency}_{to_currency}"
        if direct in rates:
            updated = rates[direct].get("updated_at", "N/A")
        elif f"{from_currency}_USD" in rates:
             updated = rates[f"{from_currency}_USD"].get("updated_at", "N/A")

        return f"Курс {from_currency}→{to_currency}: {rate:.8f} (обновлено: {updated})"

    def _load_rates(self) -> dict:
        data = load_json(RATES_FILE, {})
        if not data:
            return {k: {"rate": v, "updated_at": datetime.now().isoformat()} for k, v in MOCK_RATES.items()}
        return data

    def _check_rates_freshness(self, rates_data: dict):
        last_update_str = None
        for key, val in rates_data.items():
            if isinstance(val, dict) and "updated_at" in val:
                last_update_str = val["updated_at"]
                break
        
        if not last_update_str:
            return

        last_update = datetime.fromisoformat(last_update_str)
        ttl = self.settings.get("RATES_TTL_SECONDS", 300)
        
        if datetime.now() - last_update > timedelta(seconds=ttl):
            pass

    def _get_rate_value(self, base: str, quote: str, rates_data: dict) -> float:
        if base == quote:
            return 1.0
            
        def get_usd_rate(code):
            if code == "USD": 
                return 1.0
            if f"{code}_USD" in rates_data:
                return rates_data[f"{code}_USD"]["rate"]
            if f"USD_{code}" in rates_data:
                return 1.0 / rates_data[f"USD_{code}"]["rate"]
            return 0.0

        base_usd = get_usd_rate(base)
        quote_usd = get_usd_rate(quote)
        
        if base_usd == 0 or quote_usd == 0:
            return 0.0
            
        return base_usd / quote_usd