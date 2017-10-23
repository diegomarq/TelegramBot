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
    
    try:
        query="p_tlg_verifica_usuario @par_id_telegram="+str(client_data['chat_id'])
        row = consult_db(query)
        if(row is 'None' or str(row.retorno) == 'ER'):
            bot.send_message(chat_id = client_data['chat_id'], text='Olá ' + user.first_name + '!\n')            
            try:
                bot.send_message(chat_id = client_data['chat_id'], text='Por favor digite e informe:\n\n /site seu site')
            except Exception as e:
                print(e)
                start(bot, update)
        else:
            if(str(row.retorno) == 'OK'):
                """"""
                client_data['cd_sistema'] = (str(row.cd_sistema)).rstrip('')
                client_data['cd_usuario'] = (str(row.cd_usuario)).rstrip('')
                client_data['contact'] = (str(row.nr_telefone)).rstrip('')
                """"""
                bot.send_message(chat_id = client_data['chat_id'], text='Olá ' + user.first_name + '!\n')  
                bot.send_message(chat_id = client_data['chat_id'], text = 'Vamos às opções que eu posso te oferecer!')
                        
                button = [InlineKeyboardButton('', callback_data='noticias'), InlineKeyboardButton('Outros', callback_data='outros')]
                reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))           
                bot.send_message(chat_id = client_data['chat_id'], text = '\nPor favor, escolha uma opção:', reply_markup=reply_markup)
    except Exception as e:
        print(e)    

def get_site(bot, update, args):
    client_data['site'] = str(args[0])
    bot.send_message(chat_id = client_data['chat_id'], text='/login seu login')               
    
def get_login(bot, update, args):
    client_data['cd_usuario'] = str(args[0])
    bot.send_message(chat_id = client_data['chat_id'], text='/senha sua senha')

def get_pwd(bot, update, args):
    client_data['pwd'] = str(args[0])
    
    reply_keyboard = [[KeyboardButton('Contato', request_contact=True)]]  
    contact_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(chat_id = client_data['chat_id'], text='Agora preciso de seu contato.', reply_markup=contact_markup)    
    
def contact(bot, update):
    user_contact = update.message.contact.phone_number
    client_data['contact'] = str(user_contact)
    bot.send_message(chat_id = client_data['chat_id'], text='Obrigado!', reply_markup=ReplyKeyboardRemove())
    
    try:
        query = "p_validar_usuario_telegram @par_dir_sistema='" + client_data['site'] + "', @par_cd_usuario='"+ client_data['cd_usuario'] + "', @par_cd_senha='" + client_data['pwd'] + "'"
        print(query)
        row = consult_db(query)
        print(row)
        if(row is 'None'):
            bot.send_message(chat_id = client_data['chat_id'], text = 'Desculpe, seu usuario não foi encontrado.')
        else: 
            
            if(str(row.in_acesso_autorizado) == str('S')):
                """"""
                client_data['cd_sistema'] = str(row.cd_sistema)
                """"""
                #insert parameters in db
                isr = "p_tlg_insere_usuario @par_cd_sistema="+client_data['cd_sistema']+", @par_id_telegram="+str(client_data['chat_id'])+", @par_cd_usuario='"+(client_data['cd_usuario']).rstrip('')+"', @par_nr_telefone='"+(client_data['contact']).rstrip('')+"'" 
                resp = insert_db(isr)
                
                if(str(resp.retorno) == 'OK'):
                    bot.send_message(chat_id = client_data['chat_id'], text = 'Sucesso! Vamos às opções que eu posso te oferecer!')
                    
                    button = [InlineKeyboardButton('Receber noticias', callback_data='noticias'), InlineKeyboardButton('Outros', callback_data='outros')]
                    reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))           
                    bot.send_message(chat_id = client_data['chat_id'], text = '\nPor favor, escolha uma opção:', reply_markup=reply_markup)
                else:
                    raise Exception('db_error', 'Problem to insert info into db')
            else:
                bot.send_message(chat_id = client_data['chat_id'], text = 'Infelizmente não posso te ajudar! Seu usuario não está autorizado.')               
        
    except Exception as e:
        print(e)
        
    
def opt_client(bot, update):    
    query = update.callback_query
    bot.edit_message_text(text="Opção escolhida: %s" % query.data,
                          chat_id=client_data['chat_id'],
                          message_id=query.message.message_id)
    opcao = query.data
    if(opcao == 'noticias'):
        
        try:
            query = "p_tlg_consulta_aba_cliente @par_cd_sistema="+client_data['cd_sistema']+", @par_cd_usuario_cliente='"+client_data['cd_usuario']+"'"
            row = consult_db(query)
            if(row is 'None'):
                print('error p_tlg_consulta_aba_cliente')
            else:
                """"""
                client_data['id_conteudo'] = str(row.id_conteudo)
                """"""
                q_not = "p_conteudo_aba @par_cd_sistema="+client_data['cd_sistema']+", @par_id_conteudo="+client_data['id_conteudo']
                row = consult_db(q_not)
                if(row is 'None'):
                    print('error in p_conteudo_aba')
                else:
                    bot.send_message(chat_id=client_data['chat_id'], text=str(row.no_titulo))
            
        except Exception as e:
            print(e)
        
    else:
        button = [InlineKeyboardButton('Receber noticias', callback_data='noticias'), InlineKeyboardButton('Outros', callback_data='outros')]
        reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))           
        bot.send_message(chat_id = client_data['chat_id'], text = 'Opção inválida. Por favor, escolha outra opção.', reply_markup=reply_markup) 

def insert_db(query):
    cnxn = pyodbc.connect(CONN_STR)
    cursor = cnxn.cursor()
    
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.commit()
    except Exception as e:
        print(e)
        row = 'error'
    
    cnxn.close()    
    return(row)

      
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