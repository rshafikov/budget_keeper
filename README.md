![BUILD STATUS](https://github.com/rshafikov/budget_keeper_bot/actions/workflows/main.yaml/badge.svg)

<h1 style="text-align:center">keep-your-budget-bot</h1>

# [Budget Keeper](https://t.me/your_budget_keeper_bot)

Budget Keeper is a Telegram-based application 
designed to help users manage their personal finances by tracking income,
expenses, and budgets. 
Built with **Python**, totally **async**, 
it offers a straightforward and secure way
to organize financial data and gain insights into spending habits.

## Features

- **Transaction Management**: Add, edit, and delete expense transactions.
- **Category Tracking**: Assign transactions to customizable categories for better organization.
- **Reports**: Visualize financial data with summaries and charts.
- **User Authentication**: Secure account access with sign-up and login functionality.

## Tecnologies

- **Fully async Python**: asyncio, FastAPI, asyncpg, aiogram, SQLAlchemy(async session)
- **Caching**: Redis
- **Database**: PostgreSQL
- **CI/CD**: GitHub Actions, Docker, Docker Compose multi-stage build

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rshafikov/budget_keeper.git
   cd budget_keeper
   ```

2. **Fill the future .env of your APP*:
   ```bash
    touch .env
   
    cat > .env << EOF
    DB_HOST=db
    DB_PORT=5432
    DB_USER=user
    DB_PASS=password
    DB_NAME=budget_bot
    DB_ECHO=False
    SECRET_KEY=<generate with: openssl rand -hex 32>
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=14400
    API_URL=http://api:8000
    REDIS_URL=redis://redis:6379/
    BOT_TOKEN=<you can get it from @BotFather>
    API_PASSWORD=strongpassword
    DB_TEST=True
    EOF
   ```

3. **Start the Docker Compose**:
   ```bash
   docker compose up -d
   ```

## Usage

Open Telegram, find your recently created bot and send "/start" to him. Enjoy!