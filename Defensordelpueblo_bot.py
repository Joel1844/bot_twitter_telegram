import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import twint
from os import remove
from os import path
import datetime
import pandas as pd
import nest_asyncio
import time
nest_asyncio.apply()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


#fecha de ayer
def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today-oneday
    return str(yesterday)


def tweet(update:Update, context:CallbackContext):
    input = update.message.text.split(" ")
    if not input[0] == "tweet":
        return
    
    palabras_claves = ["defensorrd","peulloa"]
    #palabras_claves = ["defensorrd","vulnerable","defensor","derecho","pueblo","violacion","motin","carcel","educacion","medioambiente","salud","reclamo","queja","cuidadania","pobreza","usuarios","Trabajo","discriminacion","despido","fundamental","peulloa"]
    
    c = twint.Config()
    c.Since = getYesterday()
    c.Lang = "es"
    c.Near = "Republica Dominicana"
    c.Limit = 100
    c.Store_csv = True
    c.Output = "filename.csv"
    
    for palabras in palabras_claves:
        c.Search = palabras
        twint.run.Search(c)
        
        data = pd.read_csv('filename.csv')
        tweet_list = zip(list(data['link']),list(data['tweet']))
        for link, tweet in tweet_list:
            update.message.reply_text(f'{link} \n {tweet}') 

        if path.exists('filename.csv'):
            remove('filename.csv')


def main() -> None:
    try:
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater("2009767025:AAHeClxGi3tpiX55ki6PIQVTquLBUq1Vu1s")

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("tweet", tweet))
        dispatcher.add_handler(CommandHandler("echo", echo))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, tweet))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
    except Exception as e:
        time.sleep(90)
        print(e)
        print("Error de internet, esperando 120 segundos")
        main()

if __name__ == '__main__':
    main()