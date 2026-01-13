This is an educational project—a trading platform simulator. The application can download real currency and crypto rates via API and allows users to "trade" them using a virtual account.

Project Features
Accounts: Users can register and log in. Passwords are not stored in plain text; SHA-256 hashing with salt is used.

Wallet: Every user has their own balance. A starting capital of 1000 USD is provided upon registration. You can buy and sell BTC, ETH, EUR, and other currencies.

Real-time Rates: The program connects to the internet (CoinGecko and ExchangeRate-API) to fetch current market prices.

Logging: All actions (buys, sells, errors) are recorded in log files for tracking.

Data Storage: The database is simulated using simple JSON files located in the data/ folder.

Architecture & Design Patterns
The code is divided into logical layers as required by the assignment:

Core: Main business logic (balance checks, rate calculations).

Infra: Settings management and file I/O.

ParserService: A module responsible for gathering data from external APIs.

CLI: A command-line interface for user interaction.

I implemented several design patterns covered in class: Singleton (for settings), Decorator (for logging), and Strategy (for handling different APIs).

Installation and Setup
All main actions are managed via a Makefile to avoid typing long paths manually.

First Run (install dependencies and start):

Bash

make project
Standard Run (if already installed):

Bash

poetry run project
Reset Everything (delete users and balances):

Bash

rm data/*.json
CLI Commands
Once the program starts, you will see a guest> (or username>) prompt. Available commands:

register --username name --password pass — create a new account.

login --username name --password pass — log into your account.

update-rates — Important: press this to download fresh prices from the internet.

show-rates — view current prices from the local cache.

buy --currency BTC --amount 0.01 — purchase a currency using USD.

sell --currency BTC --amount 0.01 — sell a currency to receive USD.

show-portfolio — check your current wallet balances and total value.

exit — close the program.

About the Parser
The parser is a standalone module. It saves data to data/rates.json (for fast access) and data/exchange_rates.json. If an API like CoinGecko is temporarily unavailable (due to rate limits), the program will log the error but continue to run.

 
Demo
asciinema: [![asciicast](https://asciinema.org/a/y8RCtpMmmaOUYPev.svg)](https://asciinema.org/a/y8RCtpMmmaOUYPev)

Developed by student of group M25-555 Nosov Maksim