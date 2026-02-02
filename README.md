# 📈 MarketMind - Life & Finance Simulator

**University Project** | An advanced desktop application utilizing real stock market data for economic simulation and character life management.

---

## 📋 Table of Contents
* [About the Project](#-about-the-project)
* [Technologies Used](#-technologies-used)
* [Developer Instructions (Setup)](#-developer-instructions-setup)
* [User Manual](#-user-manual)
* [Internal Logic Overview](#-internal-logic-overview)
    * [Time Simulation & Mortality System](#time-simulation--mortality-system)
    * [Income Mechanics & Monthly Settlement](#income-mechanics--monthly-settlement)
    * [Prestige & Social Status System](#prestige--social-status-system)
    * [Market Movements & Event Simulation](#market-movements--event-simulation)
* [Data Documentation (JSON Schemas)](#-data-documentation-json-schemas)
* [API Integration: yfinance](#-api-integration-yfinance-yahoo-finance)
* [Developer Console & Roadmap](#-developer-console--roadmap)
* [Project Structure](#-project-structure)

---

## About the Project
MarketMind is a desktop application that allows you to step into the shoes of an investor. The system combines **real stock market data** with RPG mechanics, such as career development, character aging, and real estate trading. The player's main goal is to skillfully manage a budget, survive dynamic market crises, and achieve the prestigious status of a "Living Legend."

---

## Technologies Used
The project is built on proven Open Source solutions:
* **PyQt6**: A powerful framework used to build a modern and responsive Graphical User Interface (GUI).
* **yfinance**: A library for downloading real-time financial data from Yahoo Finance.
* **JSON**: A lightweight data format serving as the project's local database for assets and achievements.

---

## Developer Instructions (Setup)

### Prerequisites
* Python 3.10 or newer.
* Active internet connection (required for the initial stock market snapshot download).

### Installation and Start
1. Clone the repository: `git clone https://github.com/YourUser/MarketMind.git`
2. Navigate to the directory: `cd MarketMind`
3. Install dependencies: `pip install PyQt6 yfinance`
4. Run the application: `python main.py`

> **Note:** Upon the first launch, the system will download a data snapshot for approximately 100 companies and save it to the `market_data_snapshot.json` file.

---

## User Manual

### Starting the Game
After launching the app, create a character profile. The date of birth is crucial as it influences the biological probability of death as years pass in the simulation.

### Time Control
The game operates on a turn-based system – time does not flow automatically. Use the buttons in the header (`+1h`, `+1d`, `+1m`) to simulate the passage of time, which automatically updates your portfolio and transaction history.

### Financial Management
* **Markets**: Buy stocks and cryptocurrencies. Follow the **News Feed**, as random events can drastically change price trends.
* **Bank**: The system enforces timely loan repayments. In case of debt (negative balance), further time simulation is blocked until the dues are settled.

---

## Internal Logic Overview

The project implements a multi-layered simulation engine managing interactions between time, wealth, and player prestige.



### Time Simulation & Mortality System
The time engine in the `GameView` class manages the calendar and the risk of game termination:
* **Time Jumps**: Supports intervals from 1 hour to 1 month (720h).
* **Aging Mechanics**: The system calculates character age based on `date_of_birth` and the current game date.
* **Death Probability**: At every daily jump, the system rolls for a "Game Over" based on an age-related risk curve (18-100 years).
* **Final Report**: Upon death, a full asset inventory is performed (cash + real estate + vehicles + valuables) to calculate the final Net Worth.

### Income Mechanics & Monthly Settlement
Every 720 simulation hours, the `process_monthly_finances()` method acts as an automated accountant:
* **Job Income**: Calculates base salary plus seniority bonuses (*milestones*) from `jobs.json`.
* **Dividends**: Quarterly payouts based on owned stocks and their `dividend_yield` ratio.
* **Maintenance (Upkeep)**: Automatic collection of fees for properties. The `primary_home` incurs full cost, while others incur 50%.
* **Debt Servicing**: Automatic deduction of bank loan installments. Lack of funds blocks time progression.

### Prestige & Social Status System
Prestige unlocks rare achievements managed by the `AchievementManager`:
* **Fixed Assets**: Items in JSON files have assigned prestige point values.
* **Primary Home Multiplier**: The selected main residence generates a prestige bonus, key to reaching "Living Legend" status.

### Market Movements & Event Simulation
The market simulates stock exchange "life" even without new API data:
* **Volatility**: Stocks change price by ±2%, and cryptos by ±5% per day.
* **Events**: Events (e.g., a crash) apply multipliers (`impact`) to sectors, changing price trends.

---

## Data Documentation (JSON Schemas)

The application uses seven JSON files as a local database:

* **`achievements.json`**: Definitions of 49 achievements (e.g., "Aviation Beginner"). Stores titles, descriptions, and IDs.
* **`courses.json`**: Available training and certificates needed for specific career paths.
* **`events.json`**: Market event database (crashes, bull markets) that dynamically modify prices.
* **`jobs.json`**: Defines the career ladder, salary brackets, and requirements for top positions like CEO.
* **`properties.json`**: Real estate catalog with prices, `upkeep` costs, and prestige impact.
* **`valuables.json`**: Collectibles required for trophies like "Art Collector".
* **`vehicles.json`**: Vehicle database (cars, helicopters), key for collection-based achievements.

---

## API Integration: yfinance (Yahoo Finance)

The application relies on authentic market valuations fetched via the `MarketProvider` class.



### Data Fetching Mechanism
* **Initialization**: The system defines ticker lists for sectors like Tech, Defense, or Crypto.
* **History**: The `ticker.history(period="7d")` method fetches data from the last 7 trading days.
* **Optimization**: Data is serialized to `market_data_snapshot.json` for offline play and API rate-limit protection.

---

## Developer Console (Cheat Commands)

Integrated into the **SYSTEM** view (accessible via the ⚙️ button) for testing purposes:

| Command | Example | Description |
| :--- | :--- | :--- |
| `money [amount]` | `money 500000` | Adds the specified amount to the player's balance. |
| `event [id]` | `event G_CRASH_01` | Forces the immediate occurrence of a specific market event. |
| `kill` | `kill` | Triggers immediate character death and generates the End Game Report. |
| `test_luck` | `test_luck` | Displays the current percentage chances for event draws in the console. |

---

## Roadmap

MarketMind is designed for further expansion with the following modules:

1.  **Business System**: Ability to invest in startups and manage your own corporation for passive income.
2.  **Advanced Analytics**: Introduction of Candlestick Charts and technical indicators (RSI, Moving Averages).
3.  **Dynamic Education**: Expanding the course system into a skill tree where certificates unlock unique career paths.
4.  **Relationship System**: Interaction with NPCs offering unique investment opportunities or affecting living costs.

---

*Project prepared for the university course.*