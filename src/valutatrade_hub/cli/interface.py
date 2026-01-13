import shlex
import argparse
from valutatrade_hub.core.usecases import CoreService
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError, CurrencyNotFoundError, ApiRequestError
)
# импортируем наш апдейтер
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.core.utils import load_json, RATES_FILE

class CLI:
    def __init__(self):
        self.service = CoreService()
        self.running = True

    def run(self):
        print("Добро пожаловать в ValutaTrade Hub! Введите 'help' для списка команд.")
        
        while self.running:
            try:
                user_input = input(f"{self._get_prompt}> ").strip()
                if not user_input:
                    continue
                self._handle_command(user_input)
            except KeyboardInterrupt:
                print("\nВыход...")
                self.running = False
            except Exception as e:
                print(f"Критическая ошибка CLI: {e}")

    @property
    def _get_prompt(self):
        if self.service.current_user:
            return self.service.current_user.username
        return "guest"

    def _handle_command(self, user_input):
        try:
            parts = shlex.split(user_input)
        except ValueError:
            print("Ошибка: незакрытая кавычка")
            return

        command = parts[0].lower()
        args = parts[1:]

        try:
            if command == "exit":
                self.running = False
            elif command == "help":
                self._print_help()
            elif command == "register":
                self._cmd_register(args)
            elif command == "login":
                self._cmd_login(args)
            elif command == "show-portfolio":
                self._cmd_show_portfolio(args)
            elif command == "buy":
                self._cmd_buy(args)
            elif command == "sell":
                self._cmd_sell(args)
            elif command == "get-rate":
                self._cmd_get_rate(args)
            elif command == "update-rates":
                self._cmd_update_rates(args)
            elif command == "show-rates":
                self._cmd_show_rates(args)
            else:
                print(f"Неизвестная команда: {command}")

        except (InsufficientFundsError, CurrencyNotFoundError, ApiRequestError) as e:
            print(f"Ошибка: {e}")
        except ValueError as e:
            print(f"Ошибка ввода: {e}")

    def _cmd_register(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.register(parsed.username, parsed.password))
        except SystemExit:
            print("Ошибка: register --username <name> --password <pass>")

    def _cmd_login(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.login(parsed.username, parsed.password))
        except SystemExit:
            print("Ошибка: login --username <name> --password <pass>")

    def _cmd_show_portfolio(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--base", default="USD")
        try:
            parsed = parser.parse_args(args)
            print(self.service.show_portfolio(parsed.base.upper()))
        except SystemExit:
             print("Ошибка аргументов.")

    def _cmd_buy(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--currency", required=True)
        parser.add_argument("--amount", type=float, required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.buy(parsed.currency.upper(), parsed.amount))
        except SystemExit:
            print("Ошибка: buy --currency <CODE> --amount <NUM>")

    def _cmd_sell(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--currency", required=True)
        parser.add_argument("--amount", type=float, required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.sell(parsed.currency.upper(), parsed.amount))
        except SystemExit:
             print("Ошибка: sell --currency <CODE> --amount <NUM>")

    def _cmd_get_rate(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--from", dest="from_curr", required=True)
        parser.add_argument("--to", required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.get_rate(parsed.from_curr.upper(), parsed.to.upper()))
        except SystemExit:
             print("Ошибка: get-rate --from <CODE> --to <CODE>")

    def _cmd_update_rates(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--source", default=None, help="coingecko or exchangerate")
        try:
            parsed = parser.parse_args(args)
            updater = RatesUpdater()
            print(updater.run_update(specific_source=parsed.source))
        except SystemExit:
            print("Ошибка: update-rates [--source <name>]")
        except Exception as e:
            print(f"Сбой обновления: {e}")

    def _cmd_show_rates(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--currency", default=None)
        parser.add_argument("--top", type=int, default=None)
        try:
            parsed = parser.parse_args(args)
            data = load_json(RATES_FILE, {})
            pairs = data.get("pairs", {})
            
            if not pairs:
                print("Кэш курсов пуст. Сделайте update-rates.")
                return

            print(f"Курсы из кэша (обновлено: {data.get('last_refresh', 'N/A')}):")
            
            # фильтрация
            filtered = []
            for pair, info in pairs.items():
                if parsed.currency and parsed.currency.upper() not in pair:
                    continue
                filtered.append((pair, info))

            # сортировка по убыванию цены
            filtered.sort(key=lambda x: x[1]['rate'], reverse=True)

            if parsed.top:
                filtered = filtered[:parsed.top]

            for pair, info in filtered:
                print(f"- {pair}: {info['rate']:.4f} (Источник: {info['source']})")
                
        except SystemExit:
            print("Ошибка аргументов show-rates")

    def _print_help(self):
        print("""
Доступные команды:
  register --username <str> --password <str>
  login --username <str> --password <str>
  show-portfolio [--base <USD|EUR...>]
  buy --currency <CODE> --amount <float>
  sell --currency <CODE> --amount <float>
  get-rate --from <CODE> --to <CODE>
  update-rates [--source <coingecko|exchangerate>]
  show-rates [--currency <CODE>] [--top <N>]
  exit
        """)