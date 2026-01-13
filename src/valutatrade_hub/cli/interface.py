import shlex
import argparse
import sys
from valutatrade_hub.core.usecases import CoreService

class CLI:
    #класс интерфейса
    def __init__(self):
        self.service = CoreService()
        self.running = True

    def run(self):
        #главный цикл
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
                print(f"Ошибка системы: {e}")

    @property
    def _get_prompt(self):
        #промпт зависит от юзера
        if self.service.current_user:
            return self.service.current_user.username
        return "guest"

    def _handle_command(self, user_input):
        #разбор команды
        try:
            parts = shlex.split(user_input)
        except ValueError:
            print("Ошибка: незакрытая кавычка")
            return

        command = parts[0].lower()
        args = parts[1:]

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
        else:
            print(f"Неизвестная команда: {command}")

    def _cmd_register(self, args):
        #обработка register
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.register(parsed.username, parsed.password))
        except SystemExit:
            print("Ошибка: используйте register --username <name> --password <pass>")
        except ValueError as e:
            print(e)

    def _cmd_login(self, args):
        #обработка login
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.login(parsed.username, parsed.password))
        except SystemExit:
            print("Ошибка: используйте login --username <name> --password <pass>")
        except ValueError as e:
            print(e)

    def _cmd_show_portfolio(self, args):
        #обработка show-portfolio
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--base", default="USD")
        try:
            parsed = parser.parse_args(args)
            print(self.service.show_portfolio(parsed.base.upper()))
        except SystemExit:
             print("Ошибка аргументов.")
        except ValueError as e:
            print(e)

    def _cmd_buy(self, args):
        #обработка buy
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--currency", required=True)
        parser.add_argument("--amount", type=float, required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.buy(parsed.currency.upper(), parsed.amount))
        except SystemExit:
            print("Ошибка: buy --currency <CODE> --amount <NUM>")
        except ValueError as e:
            print(e)

    def _cmd_sell(self, args):
        #обработка sell
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--currency", required=True)
        parser.add_argument("--amount", type=float, required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.sell(parsed.currency.upper(), parsed.amount))
        except SystemExit:
             print("Ошибка: sell --currency <CODE> --amount <NUM>")
        except ValueError as e:
            print(e)

    def _cmd_get_rate(self, args):
        #обработка get-rate
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--from", dest="from_curr", required=True)
        parser.add_argument("--to", required=True)
        try:
            parsed = parser.parse_args(args)
            print(self.service.get_rate(parsed.from_curr.upper(), parsed.to.upper()))
        except SystemExit:
             print("Ошибка: get-rate --from <CODE> --to <CODE>")
        except Exception as e:
            print(f"Ошибка получения курса: {e}")

    def _print_help(self):
        print("""
Доступные команды:
  register --username <str> --password <str>
  login --username <str> --password <str>
  show-portfolio [--base <USD|EUR...>]
  buy --currency <CODE> --amount <float>
  sell --currency <CODE> --amount <float>
  get-rate --from <CODE> --to <CODE>
  exit
        """)