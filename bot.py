import logging
import time
import os
import cloudscraper
import json
import datetime
import requests
import telegram
import json

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

limit_time = 0

# add_1 = "😎🌜 <a href='https://t.me/dopemoonofficial'> Dopemoon </a>❗️Not a SafeMoon Fork ❕No LP tokens to Dev wallet 🔥 Ownership Renounced🐰<a href='https://exchange.pancakeswap.finance/#/swap?outputCurrency=0xC03ff4EB23a8D59978C7fCd7720f952611ddd6E4'> PancakeSwap </a> | 🌳 <a href='https://linktr.ee/dopemoon'> LinkTree </a>"
# add_2 = "⛔️👉This might be your last chance⚠️ to get <a href='https://bit.ly/2Qhucea'> $BTCR </a> 🎉 this cheap‼️Tax: | 4% Distributed 💸 | 3% Burn🔥| No Team Tokens ✅ | <a href='https://bit.ly/3y4HMTc'> Website. </a> Come have a 🐳 of a time 🥳"
# add_3 = "👩 <a href='https://www.milf.finance/'> #MILF </a> is the most exciting new launch,  <a href='https://www.coingecko.com/en/coins/milf-finance'> Coingecko </a>💆‍♀, influencers 🤳, liq 🔐, ownership renounced 🙅‍♀, dev dox. <a href='https://exchange.pancakeswap.finance/#/swap?outputCurrency=0xCB7A1Dc3a40FB64eA57D297Cef439A103fc11E66'> BUY </a> 🏃🏼 ♀ <a href='https://t.me/milffinance_official'> TG </a> 🏃🏾‍♀BEWARE COPYCATS 🙎‍♀🤦‍♀"
# add_4 = "<a href='https://t.me/x2pofficial'> X2POfficial </a> A New Revolution 💎 • LP Locked 🔒 • 6000 hodlers • 10 % to hodlers • Apple Giveaway ✅ • <a href='https://xenonpay.org/'> XenonPay.org </a>"
# add_5 = " 👑<a href='https://bit.ly/3tTtEch'>United Emirate Decentralized Coin</a>👑 Supply Only 20M! Price=$0.01 💴 Make x100 🚀 Buy On <a href='https://bit.ly/3omXLHX'> PancakeSwap </a>"

current_ad_idx = 0

ADS_FILE_NAME = 'ads.json'


def get_ads():
    try:
        file = open(ADS_FILE_NAME, 'r')
        #
        ads = json.load(fp=file)
        #
        file.close()

        return ads

    except:
        print("error opening ads.json")

        return {"count": 0, "list": []}


def update_adds(add_to_add):
    updated_adds = get_ads()

    file = open(ADS_FILE_NAME, 'w')

    updated_adds['list'].append(add_to_add)
    updated_adds['count'] = len(updated_adds['list'])

    json.dump(updated_adds, file)

    file.close()


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
    update.message.reply_text(text='<b>/p</b> or <b>/price</b> shows the price for SAFEMARSCASH.\n'
                                   '<b>/t</b> or <b>/time</b> Time until the bot will be released (anti-spam).\n'
                                   '<b>/help</b> helps you in finding the commands supported by the bot.\n\n'
                                   '<b>Sayan</b> mode:\n'
                                   '<b>/new_ad ad_to_add</b> (a string containing the new ad to be pushed to the list)\n'
                                   '<b>/get_ads</b> Shows all listed ads\n',
                              parse_mode=telegram.ParseMode.HTML
                              )


def tm_time(update, context):
    """Send a message when the command /help is issued."""

    if not allow_reply():
        time = get_reply_time()
        update.message.reply_text(text=f'Bot will be released in <b>{round(5 - time, 1)}</b> <i>sec.</i>',
                                  parse_mode=telegram.ParseMode.HTML)

        return

    update.message.reply_text(text='Bot is waiting for your command...', parse_mode=telegram.ParseMode.HTML)


def new_add(update, context):
    add = ' '.join(context.args)

    if update.message.from_user.username in ['RUSSELL829', 'doubleny']:
        update_adds(add)
        update.message.reply_text(text='Ok. I have just added it.', parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text(text='You are not allowed to do this.', parse_mode=telegram.ParseMode.HTML)


def see_all_adds(update, context):
    ads = get_ads()

    ads_list = ads['list']

    response = f'Number of ads: <b> {ads["count"]} </b> \n\n'

    for ad in ads_list:
        response += ad
        response += '\n\n'

    update.message.reply_text(text=response, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)


def get_current_add():
    global current_ad_idx

    ads = get_ads()

    if ads['count'] == 0:
        return

    current_add = ads['list'][current_ad_idx]
    current_ad_idx += 1
    current_ad_idx = current_ad_idx % ads['count']

    return current_add


def price(update, context):
    today = datetime.date.today()
    first_day = datetime.date(2021, 5, 11)

    global limit_time

    if not allow_reply():
        return

    scraper = cloudscraper.create_scraper()

    api_response = {}

    coin_name = ''
    coin_price_usd = 0
    coin_price_change = 0
    coin_mcapp = 0
    coin_mcapp_formatted = 0

    transactions_count = 0
    transactions_change = 0

    liquidity_usd = 0

    volume_usd = 0
    volume_change = 0

    coin_supply = 363.3
    url_pancake = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=0xd948a2c11626a0efc25f4e0cea4986056ac41fed&inputCurrency=BNB'
    url_bogged = 'https://bogged.finance/swap?token=0xd948A2c11626a0EFC25f4e0ceA4986056AC41feD'
    url_dexguru = 'https://dex.guru/token/0xd948a2c11626a0efc25f4e0cea4986056ac41fed-bsc'
    url_poocoin = 'https://poocoin.app/tokens/0xd948a2c11626a0efc25f4e0cea4986056ac41fed'

    error_fetching = False

    try:
        api_response = json.loads(
            scraper.get("https://api.dex.guru/v1/tokens/0xd948a2c11626a0efc25f4e0cea4986056ac41fed-bsc").text)

        coin_name = api_response['symbol']
        coin_price = float(api_response['priceUSD'] * 1e6)
        coin_price_change = api_response['priceChange24h']

        coin_mcapp = round(coin_supply * 1e6 * coin_price)
        coin_mcapp_formatted = "{:,}".format(coin_mcapp)

        transactions_count = api_response['txns24h']
        transactions_change = api_response['txns24hChange']

        liquidity_usd = api_response['liquidityUSD']

        volume_usd = api_response['volume24hUSD']
        volume_change = api_response['volumeChange24h']

    except:
        error_fetching = True
        coin_name = api_response['data']['coin_name']
        coin_price = float(api_response['data']['coin_price']) * 1e6
        coin_mcapp = round(coin_supply * 1e6 * coin_price)
        coin_mcapp_formatted = "{:,}".format(coin_mcapp)

    limit_time = time.time()

    num_days = today - first_day

    if not error_fetching:
        update.message.reply_text(text=f"         🚀   {coin_name}   🚀\n\n"
                                       f"💰  1M tokens: <b>${round(coin_price, 8)}</b><i>({round(coin_price / coin_price_change * 100)}% last 24h)</i> \n"
                                       f"💴  Market cap: <b>${coin_mcapp_formatted}</b> \n"
                                       f"💬  Transactions count (24h): <b>{round(transactions_count)}</b><i>({round(transactions_change * 100)}% last 24h)</i>\n"
                                       f"📊  Volume (24h): <b>${round(volume_usd)}</b><i>({round(volume_change * 100)}% last 24h)</i>\n"
                                       f"💸  Liquidity (24h): <b>${round(liquidity_usd)}</b>\n"
                                       f"🎚  Supply: <b>{coin_supply}t</b> \n"
                                       f"🔄  Buy/Sell on <a href='{url_pancake}'>PancakeSwapV2</a> | <a href='{url_bogged}'>Bogged</a> | <a href='{url_dexguru}'> Dex Guru</a>\n"
                                       f"〽️  Charts on 💩 <a href='{url_poocoin}'>PancakeSwapV2</a> | 📈 <a href='{url_bogged}'>Bogged</a> | 🛠 <a href='{url_dexguru}'> Dex Guru</a>\n"
                                       f"⏰  Time Since Launch {num_days.days} days\n\n"
                                       f"<i>{get_current_add()}</i>\n",
                                  parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # 1773001800:AAHtAX5DUReFenUYgwpteZCfn4S66z-KFiY

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
    dp.add_handler(CommandHandler("new_ad", new_add, pass_args=True, pass_user_data=True))
    dp.add_handler(CommandHandler("get_ads", see_all_adds))

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
