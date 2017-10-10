import telegram
from telegram.ext import Updater, CommandHandler, Job

import logging
import pyodbc 


# message to start calling bot
def start(bot, updater):
    bot.send_message(chat_id=updater.message.chat_id, text="Eu sou o bot de alerta.")
    
def login(bot, updater, args, job_queue, chat_data):
    chat_id = updater.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            updater.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data['job'] = job

        #updater.message.reply_text('Usuário sucesso')

    except (IndexError, ValueError):
        updater.message.reply_text('Login: /login <usuario>')
    
# message from the bd
def sendAlert(bot, updater):    
    bot.send_message(chat_id=updater.message.chat_id, text="")
    
# email sent today
#def radAlert(bot, updater):
#    bot.send_message(chat_id=)

def alarm(bot, updater):
    bot.send_message(chat_id=updater.message.chat_id, text="Rádio...")
    
    
def set(bot, update, args, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(bot, update, chat_data):
    """Removes the job if the user changed their mind"""

    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
    
# start connection with db
#### command to install odbc driver on linux
# sudo apt-get install unixodbc
# sudo apt-get install unixodbc-bin
# sudo apt-get install unixodbc-dev

conn_str = (
        'DRIVER={/opt/microsoft/msodbcsql/lib64/libmsodbcsql-13.1.so.9.0};'
        'SERVER=;'
        'UID=;'
        'PWD=;'
        'DATABASE=;'    
    )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()
cursor.execute("SELECT top 10 * FROM alt_alerta")

while 1:
    row = cursor.fetchone()
    if not row:
        break
    print(row)
cnxn.close()
    
# check if the user needs an answer
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

#rad_handler = CommandHandler('radio', alert_rad)
#dispatcher.add_handler(rad_handler)

def main():    
    # check bot existence
    bot = telegram.Bot(token='425927387:AAGOwjYib6TjshazA5uibYF_EnpWMRHo5YM')
    # print(bot.get_me())
    
    # frontend telegram class
#    updater = Updater(token='425927387:AAGOwjYib6TjshazA5uibYF_EnpWMRHo5YM')
    
    # set dispatcher as a telegram bot handle
#    dp = updater.dispatcher
#    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()
    

if __name__ == '__main__':
    main()

