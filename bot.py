import logging
import time
import os
import cloudscraper
import json

import requests
import math
import telegram

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
limit_time = 0


idx = 0
ticks_update_time = 0
last_hour_ticks = [0.01029474, 0.01029474, 0.01029474, 0.01029474, 0.01029474, 0.01029474]

def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


def get_reply_time():
    global limit_time

    return time.time() - limit_time


def allow_reply():
    global limit_time

    current = time.time() - limit_time

    return current >= 5

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hey this is your bot, Uncle Space Bot!\n'
                              'I am glad to serve you with most updated info.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(text='<b>/p</b> or <b>/price</b> shows the price for SAFESPACE from pancakeSwap.\n'
                              '<b>/help</b> helps you in finding the commands supported by the bot\n',
                              parse_mode=telegram.ParseMode.HTML
                              )


def tm_time(update, context):
    """Send a message when the command /help is issued."""

    if not allow_reply():
        time = get_reply_time()
        update.message.reply_text(text=f'Bot will be released in <b>{round(5 - time,1)}</b> <i>sec.</i>',
                                  parse_mode=telegram.ParseMode.HTML)

        return

    update.message.reply_text(text='Bot is waiting for your command...',  parse_mode=telegram.ParseMode.HTML)


def price(update, context):
    global limit_time

    if not allow_reply():
        return

    # scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
    scraper = cloudscraper.create_scraper()

    # r = requests.get(url="https://api.pancakeswap.info/api/v2/tokens/0xe1DB3d1eE5CfE5C6333BE96e6421f9Bd5b85c987")
    # response = r.json()

    response = {}
    name = ''
    price = 0
    mcapp = 0
    formatted_market_cap = 0
    transactions_count = 0
    transactions_change = 0
    volume_usd = 0
    volume_change = 0
    price_usd = 0
    price_change = 0
    err = False

    try:
        resJson = json.loads(scraper.get("https://api.dex.guru/v1/tokens/0xd948a2c11626a0efc25f4e0cea4986056ac41fed-bsc").text)
        print(resJson)
        name = resJson['symbol']
        # transactions_count = resJson['txns24h']
        # transactions_change = resJson['txns24hChange']
        # volume_usd = resJson['volume24hUSD']
        # volume_change = resJson['volumeChange24h']
        price = float(resJson['priceUSD'] * 1e6)
        price_change = resJson['priceChange24h']

        mcapp = round(363.3 * 1e6 * price)
        formatted_market_cap = "{:,}".format(mcapp)
        supply = 363.3

    except:
        err = True
        print("error")
        name = response['data']['name']
        price = float(response['data']['price']) * 1e6
        mcapp = round(363.3 * 1e6 * price)
        formatted_market_cap = "{:,}".format(mcapp)

    limit_time = time.time()

    if err:
        update.message.reply_text(text=f"         🚀   {name}   🚀\n\n"
                                   f"💰  1M tokens: <b>${round(price, 8)}</b><i>({round(price / price_change * 100)}% last 24h)</i> \n"
                                   f"💴  Market cap: <b>${formatted_market_cap}</b> \n"
                                   f"💴  Supply: <b>{supply}t</b> \n",
                                  parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text(text=f"         🚀   {name}   🚀\n\n"
                                           f"💰  1M tokens: <b>${round(price, 8)}</b><i>({round(price / price_change * 100)}% last 24h)</i> \n"
                                           f"💴  Market cap: <b>${formatted_market_cap}</b> \n"
                                           f"💴  Supply: <b>{supply}t</b> \n",
                                  parse_mode=telegram.ParseMode.HTML)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    #1773001800:AAHtAX5DUReFenUYgwpteZCfn4S66z-KFiY

    # updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    updater = Updater('1773001800:AAHtAX5DUReFenUYgwpteZCfn4S66z-KFiY', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("p", price))
    dp.add_handler(CommandHandler("time", tm_time))
    dp.add_handler(CommandHandler("t", tm_time))

    # dp.add_handler(CommandHandler("price_bogged", priceB))
    # dp.add_handler(CommandHandler("p_bogged", priceB))
    #
    # dp.add_handler(CommandHandler("price_pancake", priceP))
    # dp.add_handler(CommandHandler("p_pancake", priceP))
    # log all errors
    dp.add_error_handler(error)

    global ticks_update_time
    global limit_time

    ticks_update_time = time.time()

    limit_time = time.time()
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
