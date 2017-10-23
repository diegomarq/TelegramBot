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
jb = updater.job_queue
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
                bot.send_message(chat_id = client_data['chat_id'], text='Por favor digite e informe:\n\n /login seu login')
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
                """"""
                query = "select * from UsuarioSistema where LogUsr = '" + client_data['cd_usuario'] + "'"
                row = consult_db(query)
                
                if(row is 'None'):
                    print('Problema ao checar login')
                else:
                    """
                    user data storage
                    """
                    client_data['cd_praca'] = row.cd_praca
                    client_data['sg_departamento'] = row.sg_departamento
                    """"""""""""""""""""""""""""""
                    if(client_data['sg_departamento'] is 'None'):
                        bot.send_message(chat_id = client_data['chat_id'], text='Verifiquei que você não está em um departamento. Por favor, peça ao pessoal do administrativo que te cadastre.')
                    else:
                        bot.send_message(chat_id = client_data['chat_id'], text='Verifiquei que você é do departamento de '+ client_data['sg_departamento'])
                        
                        query = "select * from alt_alerta_departamento dp inner join alt_alerta al on al.id_alerta = dp.id_alerta and al.st_alerta = 'A' where dp.cd_praca = '"+ client_data[
                                'cd_praca'] + "' and dp.sg_departamento = '" + client_data['sg_departamento'] + "'"
                        row = consult_db_list(query)                            
                        if(row is 'None'):
                            bot.send_message(chat_id = client_data['chat_id'], text='Desculpe! Não há alertas cadastrados para o seu departamento.')
                        else:
                            actions = dict()
                            for i in row:
                               actions[i.id_alerta] = i.ds_alerta
                               
                            button_list = [InlineKeyboardButton(v, callback_data=k) for k, v in actions.items()]         
                            reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
                            bot.send_message(chat_id = client_data['chat_id'], text='Clique no alerta que você quer monitorar:\n', reply_markup=reply_markup)                                
    except Exception as e:
        print(e)
    
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
        query = "p_validar_usuario_telegram @par_dir_sistema='SMI', @par_cd_usuario='"+ client_data['cd_usuario'] + "', @par_cd_senha='" + client_data['pwd'] + "'"
        row = consult_db(query)
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
                    
                    """"""
                    query = "select * from UsuarioSistema where LogUsr = '" + client_data['cd_usuario'] + "'"
                    row = consult_db(query)
                    
                    if(row is 'None'):
                        print('Problema ao checar login')
                    else:
                        """
                        user data storage
                        """
                        client_data['cd_praca'] = row.cd_praca
                        client_data['sg_departamento'] = row.sg_departamento
                        """"""""""""""""""""""""""""""
                        if(client_data['sg_departamento'] is 'None'):
                            bot.send_message(chat_id = client_data['chat_id'], text='Verifiquei que você não está em um departamento. Por favor, peça ao pessoal do administrativo que te cadastre.')
                        else:
                            bot.send_message(chat_id = client_data['chat_id'], text='Verifiquei que você é do departamento de '+ client_data['sg_departamento'])
                            
                            query = "select * from alt_alerta_departamento dp inner join alt_alerta al on al.id_alerta = dp.id_alerta and al.st_alerta = 'A' where dp.cd_praca = '"+ client_data[
                                    'cd_praca'] + "' and dp.sg_departamento = '" + client_data['sg_departamento'] + "'"
                            row = consult_db_list(query)                            
                            if(row is 'None'):
                                bot.send_message(chat_id = client_data['chat_id'], text='Desculpe! Não há alertas cadastrados para o seu departamento.')
                            else:
                                actions = dict()
                                for i in row:
                                   actions[i.id_alerta] = i.ds_alerta
                                   
                                button_list = [InlineKeyboardButton(v, callback_data=k) for k, v in actions.items()]         
                                reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
                                bot.send_message(chat_id = client_data['chat_id'], text='Clique no alerta que você quer monitorar:\n', reply_markup=reply_markup)                                
                    
                else:
                    raise Exception('db_error', 'Problem to insert info into db')
            else:
                bot.send_message(chat_id = client_data['chat_id'], text='Infelizmente não posso te ajudar! Seu usuario não está autorizado.')               
        
    except Exception as e:
        print(e)
        
    
def opt_client(bot, update):    
    query = update.callback_query
    bot.edit_message_text(text="Opção escolhida: %s" % query.data,
                          chat_id=client_data['chat_id'],
                          message_id=query.message.message_id)
    client_data['id_alerta'] = query.data
    try:
        query = "select no_sp from alt_conteudo_alerta c inner join alt_alerta a on a.id_conteudo = c.id_conteudo where a.id_alerta = " + str(client_data['id_alerta'])
        row = consult_db(query)
        client_data['sp'] = str(row.no_sp)
        bot.send_message(chat_id = client_data['chat_id'], text=client_data['sp'])
    except Exception as e:
        print(e)
    
    bot.send_message(chat_id = client_data['chat_id'], text='Ok. Agora você irá receber os alertas por aqui!')
    jb.run_repeating(callback_minute, interval=1, first=0)
    
def callback_minute(bot, job):
    try:
        alert = consult_db(client_data['sp'])
        if(alert is 'None'):
            print('Nenhum problema encontrado')
        else:
            bot.send_message(chat_id = client_data['chat_id'], text='Id: '+ str(alert.id_coleta) +', dt_final: '+ str(alert.dt_final))
    except Exception as e:
        print(e)
    
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