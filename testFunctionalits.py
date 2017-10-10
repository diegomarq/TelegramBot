#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 11:21:51 2017

@author: diego
"""

from telegram import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

import pyodbc 

CONN_STR = ()

CONTACT = range(4)

def start(bot, update):
    # Check if it is possible search person only by name and last name
    user = update.message.from_user 
    
#    query = "EXECUTE p_erp_funcionario_busca '" + user.first_name + ' ' +  user.last_name + "'"    
#    row = consult_db(query)        
    row = 'None'
    
    if(row is 'None'):
        reply_keyboard = [[KeyboardButton('Contato', request_contact=True)]]  
        update.message.reply_text(
            'Olá!\nPara que eu possa te ajudar preciso que você me dê algumas informações.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        #consult_db()
    else:
        update.message.reply_text('Olá ' + row.no_funcionario)
    
    return CONTACT

def contact(bot, update):
#    user = update.message.from_user
    user_contact = update.message.contact.phone_number
    
    query = "select top 1 * from erp_contato where (nr_telefone_trabalho like '%" + user_contact + "%') and st_contato = 'A'"
    row = consult_db(query)        
    
    if(row is 'None'):
        update.message.reply_text('Olá ' + row.no_contato, reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Desculpa, o sistema não identificou seu nome. Por favor contacte a empresa.', reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Para me desativar digite: /desativar')
    
    
def consult_db(query):
    cnxn = pyodbc.connect(CONN_STR)
    cursor = cnxn.cursor()
    
    try:
        cursor.execute(query)   
        row = cursor.fetchone()        

#        while 1:
#            row = cursor.fetchone()
#            if not row:
#                break
#            print(row.no_funcionario)
        
    except Exception as e:
        print(e)
        row = ''
    
    return(row)
    cnxn.close()    
    
def cancel(bot, update):
    user = update.message.from_user    
    update.message.reply_text('Tchau %S!', user.first_name)
    return ConversationHandler.END

def main():
    
    updater = Updater('425927387:AAGOwjYib6TjshazA5uibYF_EnpWMRHo5YM')
    dp = updater.dispatcher
    
#    dp.add_handler(CommandHandler('start', start))    
#    dp.add_handler(MessageHandler(Filters.contact, contact))
    
    conv_handler = ConversationHandler(            
            entry_points = [CommandHandler('start', start)], 
            
            states = {
                    CONTACT: [MessageHandler(Filters.contact, contact)]
            },
            
            fallbacks = [CommandHandler('desativar', cancel)]            
    )
    
    # Add commands to the dispatcher
    dp.add_handler(conv_handler)
    
    # By default poll_interval = 0, timeout = 10
    updater.start_polling()
    
    # Stops execution with ctrl+c
    updater.idle()
    
if __name__ == '__main__':
    main()