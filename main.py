import asyncio
import os
import datetime
import json
import requests
import pytz
import openai
from openai import InvalidRequestError
from typing import Dict, Any
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

EOD_API_KEY = os.getenv("EOD_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


openai.api_key = OPENAI_API_KEY

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def on_startup(dp):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Bot has been started")

async def on_shutdown(dp, scheduler):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Bot has been stopped")

    # Remove all handlers
    dp.message_handlers.clear()

    # Close bot and dispatcher
    await dp.storage.close()
    await dp.storage.wait_closed()

    # Close scheduler
    scheduler.shutdown()

    # Close connections
    await bot.session.close()

# Command handlers
import requests

import requests

async def verify_symbol(symbol):
    API_URL = f"https://eodhistoricaldata.com/api/news?api_token={EOD_API_KEY}&s={symbol}.US&&limit=10"

    response = requests.get(API_URL)
    data = response.json()

    if data:  # Check if the response has any data (i.e., the symbol exists)
        return True
    return False


@dp.message_handler(commands=['add_company'])
async def add_company(message: types.Message):
    input_symbols = message.get_args().replace(",", " ").split()
    symbols = [symbol.upper() for symbol in input_symbols]

    COMPANIES = load_ticker_list()

    added_symbols = []
    existing_symbols = []
    invalid_symbols = []

    for symbol in symbols:
        if symbol in COMPANIES:
            existing_symbols.append(symbol)
        else:
            if await verify_symbol(symbol):
                COMPANIES[symbol] = None  # No company name is stored
                added_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)

    save_ticker_list(COMPANIES)

    response_text = ""
    if added_symbols:
        response_text += f"Added {', '.join(added_symbols)} to the list."
    if existing_symbols:
        response_text += f"\n{', '.join(existing_symbols)} already exist in the list."
    if invalid_symbols:
        response_text += f"\n{', '.join(invalid_symbols)} are not valid symbols."

    await message.reply(response_text.strip())



@dp.message_handler(commands=['remove_company'])
async def remove_company(message: types.Message):
    symbol = message.get_args().split()[0].upper()

    COMPANIES = load_ticker_list()

    if symbol not in COMPANIES:
        await message.reply(f"{symbol} is not in the list.")
    else:
        COMPANIES.pop(symbol)
        save_ticker_list(COMPANIES)
        await message.reply(f"Removed {symbol} from the list.")

@dp.message_handler(commands=['list_companies'])
async def list_companies(message: types.Message):
    companies = load_ticker_list()  # Load the latest ticker list from the JSON file
    if not companies:
        await message.reply("No companies in the list.")
    else:
        company_list = "\n".join([f"{symbol}" for symbol in companies.keys()])
        await message.reply(f"List of companies:\n{company_list}")

@dp.message_handler(commands=['get_list_sentiments'])
async def get_sentiments(message: types.Message):
    global COMPANIES  # Declare the global variable to modify it
    COMPANIES = load_ticker_list()  # Load the latest ticker list from the JSON file

    if not COMPANIES:
        await message.reply("The list of companies is empty.")
    else:
        await analyze_sentiments_for_companies(COMPANIES)

@dp.message_handler(commands=['get_sentiment'])
async def get_sentiment(message: types.Message):
    symbols_arg = message.get_args()
    symbols = [symbol.strip().upper() for symbol in symbols_arg.split(',')]

    if not symbols:
        await message.reply("Please provide at least one company symbol separated by commas.")
    else:
        companies = {symbol: symbol for symbol in symbols}
        await analyze_sentiments_for_companies(companies)


def parse_companies_input(input_str: str) -> Dict[str, str]:
    companies = {}
    company_pairs = input_str.split(';')
    for pair in company_pairs:
        pair_items = pair.split(',')
        if len(pair_items) != 2:
            continue
        symbol = pair_items[0].strip().upper()
        name = pair_items[1].strip()
        companies[symbol] = name
    return companies



@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    message_text = ("Here are the available commands:\n\n"
                    "/get_list_sentiments - Run sentiment analysis on stocks being tracked.\n\n"
                    "/list_companies - List all the companies currently being tracked.\n\n"
                    "/add_company <company_ticker or comma-separated list of tickers> Add a company or multiple to the tracking list. Replace <company_ticker> with the actual stock ticker.\n\n"
                    "Example: /add_company MSFT, TSLA, SBUX\n\n"
                    "/remove_company <company_ticker> - Remove a company from the tracking list. Replace <company_ticker> with the stock ticker.\n\n"
                    "/get_sentiment <comma-separated list of tickers> - Get sentiments for a list of companies that may or may not be in your list.\n"
                    "Example: /get_sentiment AAPL, MSFT, TSLA\n\n"
                    "\nOther Examples:\n"
                    "/add_company AAPL Apple\n"
                    "/remove_company APPL")
    await message.reply(message_text)

def get_news_headlines_for_companies(companies: Dict[str, str]):
    headlines = {}
    for symbol in companies.items():
        url = f"https://eodhistoricaldata.com/api/news?api_token={EOD_API_KEY}&s={symbol}.US&&limit=100"

        response = requests.get(url)

        try:
            all_headlines = response.json()
        except json.JSONDecodeError:
            print(f"Error decoding JSON for {symbol}: {response.content}")
            all_headlines = []

        est = pytz.timezone("US/Eastern")
        utc = pytz.UTC

        start_time = datetime.datetime.strptime(yesterday_9am_est(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=est).astimezone(utc)
        end_time = datetime.datetime.strptime(today_9am_est(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=est).astimezone(utc)

        filtered_headlines = [headline for headline in all_headlines if start_time <= datetime.datetime.strptime(headline["date"], "%Y-%m-%dT%H:%M:%S%z") <= end_time]

        headlines[symbol] = filtered_headlines

    return headlines

def perform_sentiment_analysis(company,  headline):
    print(headline)
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer “Positive” if good news, “Negative” if bad news, or “Neutral” if uncertain in the first line. Provide no other context. Is this headline good or bad for the stock price of {company} in the short term? \n Headline: {headline}" }
        ],
        temperature=0.2,
        )
    except InvalidRequestError as e:
        return f"Error: {e}"
    sentiment = response["choices"][0]["message"]["content"]
    print(sentiment)
    return sentiment

def assign_sentiment_score(sentiment):
    sentiment = sentiment.lower()
    if "positive" in sentiment:
        return 1
    elif "neutral" in sentiment:
        return 0
    elif "negative" in sentiment:
        return -1
    else:
        return 0

async def send_summary_message(sentiment_scores):
    message = "Daily Stock Sentiment Summary:\n\n"
    for company, score in sentiment_scores.items():
        message += f"{company}: {score}\n"
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

async def analyze_sentiments_for_companies(companies):
    headlines = get_news_headlines_for_companies(companies)
    sentiment_scores = {}

    for company, company_headlines in headlines.items():
        num_headlines = len(company_headlines)
        print(f"{company}: {num_headlines} headlines")

        if num_headlines == 0:
            sentiment_scores[company] = "0 headlines"
        else:
            scores = []
            for headline in company_headlines:
                print("Sending headline for analysis")
                sentiment = perform_sentiment_analysis(company, headline["title"])
                score = assign_sentiment_score(sentiment)
                scores.append(score)
            average_score = sum(scores) / len(scores) if scores else 0
            sentiment_scores[company] = round(average_score, 2)

    await send_summary_message(sentiment_scores)


def today_9am_est():
    return datetime.datetime.now(pytz.timezone("US/Eastern")).replace(hour=9, minute=25, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

def yesterday_9am_est():
    return (datetime.datetime.now(pytz.timezone("US/Eastern")) - datetime.timedelta(days=1)).replace(hour=9, minute=31, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

async def run_scheduler():
    scheduler = AsyncIOScheduler()

    # Schedule analyze_sentiments_for_companies() to run from Monday to Friday at 9 AM US/Eastern
    scheduler.add_job(lambda: asyncio.create_task(analyze_sentiments_for_companies(COMPANIES)), "cron", day_of_week="mon-fri", hour=9, minute=0, timezone="US/Eastern")

    # Start the scheduler
    await scheduler.start()


def load_ticker_list():
    default_companies = {
        "AAPL": "Apple Inc.",
    }

    if not os.path.exists("tickers.json"):
        return default_companies

    with open("tickers.json", "r") as f:
        loaded_companies = json.load(f)

    # Merge the default_companies with loaded_companies
    merged_companies = {**default_companies, **loaded_companies}
    return merged_companies

COMPANIES = load_ticker_list()

def save_ticker_list(companies):
    with open("tickers.json", "w") as f:
        json.dump(companies, f)



# Add this function to register the command handler with the bot
def main():
    from aiogram import executor

    # Schedule analyze_sentiments_for_companies() to run from Monday to Friday at 9 AM US/Eastern
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(analyze_sentiments_for_companies(COMPANIES)), "cron", day_of_week="mon-fri", hour=9, minute=0, timezone="US/Eastern")
    scheduler.start()

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)


if __name__ == '__main__':
    main()