#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 11:21:51 2017

@author: diego
"""
#import logging

from telegram import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)
import pyodbc 

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

""""""
updater = Updater('425927387:AAGOwjYib6TjshazA5uibYF_EnpWMRHo5YM')
dp = updater.dispatcher
#jb = updater.job_queue
""""""

CONN_STR = (
    )

LOGIN_INFO = range(4)
PWD_INFO = range(4)
CLIENT_OPT = range(4)

client_data = dict()

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def start(bot, update):
    # Check if it is possible search person only by name and last name
    user = update.message.from_user    
    client_data['chat_id'] = update.message.chat_id
    print(client_data['chat_id'])
    
    bot.send_message(chat_id = client_data['chat_id'], text='Olá ' + user.first_name + '!\nPara que eu possa te ajudar, preciso de mais algumas informações.')
    bot.send_message(chat_id = client_data['chat_id'], text='Por favor digite e informe:\n\n /site seu site')
    
def get_site(bot, update, args):
    client_data['site'] = args[0]
    bot.send_message(chat_id = client_data['chat_id'], text='/login seu login')
    
    
def get_login(bot, update, args):
    client_data['login'] = args[0]
    bot.send_message(chat_id = client_data['chat_id'], text='/senha sua senha')

def get_pwd(bot, update, args):    
    client_data['pwd'] = args[0]    
    
    reply_keyboard = [[KeyboardButton('Contato', request_contact=True)]]  
    contact_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(chat_id = client_data['chat_id'], text='Agora preciso de seu contato.', reply_markup=contact_markup)    
    
def contact(bot, update):
    user_contact = update.message.contact.phone_number
    client_data['contact'] = user_contact
    bot.send_message(chat_id = client_data['chat_id'], text='Obrigado!', reply_markup=ReplyKeyboardRemove())
    
    try:
        query = "p_validar_usuario_telegram @par_dir_sistema='" + client_data['site'] + "', @par_cd_usuario='"+ client_data['login'] + "', @par_cd_senha='" + client_data['pwd'] + "'"
        print(query)
        row = consult_db(query)
        if(row is 'None'):
            bot.send_message(chat_id = client_data['chat_id'], text = 'Desculpe, seu usuario não foi encontrado.')
        else:
            print('Retorno:' + row.in_acesso_autorizado)
            if(str(row.in_acesso_autorizado) == 'S'):
                """"""
                client_data['cd_sistema'] = row.cd_sistema
                """"""            
                bot.send_message(chat_id = client_data['chat_id'], text = 'Sucesso! Vamos às opções que eu posso te oferecer!')
                
                button = [InlineKeyboardButton('Receber noticias', callback_data='noticias'), InlineKeyboardButton('Outros', callback_data='outros')]
                reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))           
                bot.send_message(chat_id = client_data['chat_id'], text = '\nPor favor, escolha uma opção:', reply_markup=reply_markup)         
            else:
                bot.send_message(chat_id = client_data['chat_id'], text = 'Infelizmente não vou poder te ajudar! Seu usuario não está autorizado.')
        
    except Exception as e:
        print(e)
    
def opt_client(bot, update):    
    query = update.callback_query
    bot.edit_message_text(text="Opção escolhida: %s" % query.data,
                          chat_id=client_data['chat_id'],
                          message_id=query.message.message_id)
    opcao = query.data
    if(opcao == 'noticias'):
        bot.send_message(chat_id=client_data['chat_id'], text='Para esta opção')
    else:
        bot.send_message(chat_id=client_data['chat_id'], text= 'Opção inválida. Por favor, escolha outra opção.')
        button = [InlineKeyboardButton('Receber noticias', callback_data='noticias'), InlineKeyboardButton('Outros', callback_data='outros')]
        reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))           
        bot.send_message(chat_id = client_data['chat_id'], text = 'Por favor, escolha uma opção:', reply_markup=reply_markup) 
        
      
def consult_db(query):
    cnxn = pyodbc.connect(CONN_STR)
    cursor = cnxn.cursor()
    
    try:
        cursor.execute(query)
        row = cursor.fetchone()
    except Exception as e:
        print(e)
        row = 'None'
    
    cnxn.close()    
    return(row)

def consult_db_list(query):
    cnxn = pyodbc.connect(CONN_STR)
    cursor = cnxn.cursor()
    
    try:
        cursor.execute(query)
        row = cursor.fetchall()        
    except Exception as e:
        print(e)
        row = 'None'
    
    cnxn.close()
    return(row)

def main():
    # Start
    dp.add_handler(CommandHandler('start', start))
    
    # Get user site
    dp.add_handler(CommandHandler('site', get_site, pass_args=True))
    
    # Get user login
    dp.add_handler(CommandHandler('login', get_login, pass_args=True))
    
    # Get user pwd
    dp.add_handler(CommandHandler('senha', get_pwd, pass_args=True))
    
    # Get client options
    dp.add_handler(CallbackQueryHandler(opt_client))
    
    # Get contact
    dp.add_handler(MessageHandler(Filters.contact, contact))
 
    # By default poll_interval = 0, timeout = 10
    updater.start_polling()
    
    # Stops execution with ctrl+c
    updater.idle()
    
if __name__ == '__main__':
    main()