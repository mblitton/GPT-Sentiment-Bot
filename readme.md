# Stock Sentiment Analysis Telegram Bot

This Telegram bot allows you to track stock sentiment for a list of companies. It fetches news headlines related to the stocks and uses OpenAI's GPT-3.5-turbo model to analyze the sentiment of each headline. The bot then calculates an average sentiment score for each stock and sends a daily summary message to a specified chat.

## Features

-   Add and remove companies from the tracking list
-   List all the companies currently being tracked
-   Run sentiment analysis on the tracked companies
-   Daily sentiment summary messages

## Installation

1.  Clone the repository:
    
    bashCopy code
    
    `git clone https://github.com/your-repo/stock-sentiment-analysis-bot.git cd stock-sentiment-analysis-bot`
    
2.  Install the required packages:
    
    Copy code
    
    `pip install -r requirements.txt`
    
3.  Set up environment variables:
    
    -   Create a `.env` file in the root directory of the project.
        
    -   Add the following environment variables with your API keys and Telegram chat ID:
        
        makefileCopy code
        
        `EOD_API_KEY=your_eod_historical_data_api_key OPENAI_API_KEY=your_openai_api_key TELEGRAM_BOT_TOKEN=your_telegram_bot_token TELEGRAM_CHAT_ID=your_telegram_chat_id`
        

## Usage

1.  Start the bot:
    
    cssCopy code
    
    `python main.py`
    
2.  Interact with the bot using the following commands:
    
    -   `/add_company <company_ticker> <company_name>`: Add a company to the tracking list.
    -   `/remove_company <company_ticker>`: Remove a company from the tracking list.
    -   `/list_companies`: List all the companies currently being tracked.
    -   `/get_sentiments`: Run sentiment analysis on the tracked companies.

## Example Commands

-   Add a company to the list: `/add_company AAPL Apple`
-   Remove a company from the list: `/remove_company AAPL`
-   List all the companies: `/list_companies`
-   Get stock sentiments: `/get_sentiments`

If you have any questions, need assistance, or want to request new features for the Stock Sentiment Analysis Telegram Bot, please feel free to open an issue on the GitHub repository or contact the bot developer.

## Contributing

We welcome contributions to improve the Stock Sentiment Analysis Telegram Bot. If you'd like to contribute, please follow these steps:

1.  Fork the repository on GitHub.
2.  Create a new branch for your changes.
3.  Make your changes and commit them with descriptive commit messages.
4.  Push your changes to your fork.
5.  Create a pull request from your fork to the original repository.

Before creating a pull request, please make sure your changes are well-documented and tested.

## Acknowledgements

The Stock Sentiment Analysis Telegram Bot uses:

-   [OpenAI's GPT-3.5-turbo model](https://beta.openai.com/docs/models/gpt-3.5-turbo) for sentiment analysis
-   [EOD Historical Data API](https://eodhistoricaldata.com/) for fetching news headlines
-   [Aiogram](https://docs.aiogram.dev/en/latest/index.html) for the Telegram bot framework
-   [APScheduler](https://apscheduler.readthedocs.io/en/stable/) for scheduling daily sentiment summary messages

We would like to thank the developers and maintainers of these libraries and services for their contributions to the open-source community.

## License

This project is licensed under the MIT License.