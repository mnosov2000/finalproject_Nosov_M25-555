# finalproject_Nosov_M25-555

# ValutaTrade Hub 

Coursework project: A trading platform simulator with real-time currency rates.
The application allows users to register, manage a multi-currency wallet, and trade (buy/sell) currencies using actual market data.

##  Features

* **Registration & Login:** User system with password hashing (SHA-256 + salt).
* **Multi-currency Wallet:** Support for USD, EUR, RUB, BTC, ETH, and others. Base currency is USD.
* **Real-time Rates:** The parser collects data from CoinGecko (crypto) and ExchangeRate-API (fiat).
* **Trading:** Buy and sell currencies with automatic cross-rate conversion.
* **History:** Logging of user operations and rate history tracking.

##  Tech Stack & Architecture

The project is written in **Python 3.12** using **Poetry** for dependency management.

The code implements the following architectural patterns:
* **Singleton:** For settings loading (`SettingsLoader`).
* **Decorator:** For logging user actions (`@log_action`).
* **Strategy:** For handling different APIs in the parser (`CoinGeckoClient`, `ExchangeRateApiClient`).
* **Layered Architecture:** Separation into `Core` (business logic), `Infra` (data), `ParserService` (external APIs), and `CLI` (interface).

Data is stored in JSON files in the `data/` folder (database emulation).

##  Installation & Usage

For convenience, all commands are collected in the `Makefile`.

1.  **Installation and First Run:**
    ```bash
    make project
    ```
    *(This command installs dependencies, sets up the environment, and starts the app)*

2.  **Run (without reinstalling):**
    ```bash
    poetry run project
    ```

3.  **Data Cleanup (Reset Database):**
    ```bash
    # Warning! This deletes all users and wallets
    rm data/*.json
    ```

## CLI Commands

After launching, you will enter the application console (`guest>` or `username>`). Type `help` for a list of commands.

| Command | Description | Example |
| :--- | :--- | :--- |
| `register` | Register a new user | `register --username max --password 123` |
| `login` | Log in to the system | `login --username max --password 123` |
| `update-rates` | **Download fresh rates from the internet** | `update-rates` |
| `show-rates` | Show current rates from cache | `show-rates --top 5` or `show-rates --currency RUB` |
| `buy` | Buy currency with USD | `buy --currency BTC --amount 0.05` |
| `sell` | Sell currency (receive USD) | `sell --currency BTC --amount 0.05` |
| `show-portfolio` | Show wallet balance | `show-portfolio` |
| `get-rate` | Get rate for a specific pair | `get-rate --from BTC --to USD` |
| `exit` | Exit the program | `exit` |

## ℹ️ Parser Service Details

The parser operates as a separate service. It downloads rates and saves them to `data/rates.json` (cache for the Core) and `data/exchange_rates.json` (history).
If one source (e.g., CoinGecko) is unavailable, the program continues working with data from other sources or logs the error.
API keys and settings are located in `src/valutatrade_hub/infra/settings.py`.


Developed by student of group M25-555 Nosov Maksim