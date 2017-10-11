#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 11:21:51 2017

@author: diego
"""

from telegram import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

import pyodbc 

CONN_STR = (
           
    )

CONTACT = range(4)
ADMIN_OPTION = range(4)

#keyboard = [[InlineKeyboardButton("Monitorar Alerta", callback_data='Alerta'), InlineKeyboardButton(
#        "Outros", callback_data='Outros')]]
#opt_markup = InlineKeyboardMarkup(keyboard)

reply_keyboard = [['Alerta'], ['Outros']]
opt_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

funcionary_data = dict()
client_data = dict()

def start(bot, update):
    # Check if it is possible search person only by name and last name
    user = update.message.from_user 
    
    query = "EXECUTE p_erp_funcionario_busca '" + user.first_name + ' ' +  user.last_name + "'"    
    row = consult_db(query)            
    
    if(row is 'None'):
        reply_keyboard = [[KeyboardButton('Contato', request_contact=True)]]  
        update.message.reply_text(
            'Olá!\nPara que eu possa te ajudar preciso que você me dê algumas informações.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return CONTACT
    else:
        """
        user data storage
        """
        funcionary_data['id_funcionario'] = row.id_funcionario
        funcionary_data['no_funcionario'] = row.no_funcionario
        
        """"""""""""""""""""""""""""""
        
        first_name = (row.no_funcionario).partition(' ')[0]
        update.message.reply_text('Olá ' + first_name)
        update.message.reply_text('Por favor, escolha uma opção na qual posso te ajudar.', reply_markup=opt_markup)
        return ADMIN_OPTION
    

def contact(bot, update):
#    user = update.message.from_user
    user_contact = update.message.contact.phone_number
    
    query = "select top 1 * from erp_contato where (nr_telefone_trabalho like '%" + user_contact + "%') and st_contato = 'A'"
    row = consult_db(query)
    
    if(row is 'None'):
        update.message.reply_text('Desculpa, o sistema não identificou seu nome. Por favor contacte a empresa.', reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Para me desativar digite: /desativar')
    else:
        """
        user data storage
        """
        client_data['id_contato'] = row.id_contato
        client_data['no_contato'] = row.no_contato
        
        """"""""""""""""""""""""""""""
        update.message.reply_text('Olá ' + row.no_contato, reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Por favor, escolha uma opção na qual posso te ajudar.', reply_markup=opt_markup)
#        return ADMIN_OPTION
        
def func_option(bot, update, user_data):
#    query = update.callback_query
#    bot.edit_message_text(text="Selected option: %s" % query.data, chat_id=query.message.chat_id, 
#                          message_id=query.message.message_id)   

    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text('Opcao escolhida: ' + text, reply_markup=ReplyKeyboardRemove())
    
    first_name = (funcionary_data['no_funcionario']).partition(' ')[0]    
    id_func = funcionary_data['id_funcionario']
    
    query = "select * from UsuarioSistema where id_funcionario = " + str(id_func)
    
    try:
        row = consult_db(query)
    except Exception as e:
        print(e)
    
    if(row is 'None'):
        print('consult is empty')
    else:
        """
        user data storage
        """
        funcionary_data['cd_praca'] = row.cd_praca
        funcionary_data['sg_departamento'] = row.sg_departamento
        
        """"""""""""""""""""""""""""""
        update.message.reply_text('%s, verifiquei que você é do departamento de: %s' % first_name, funcionary_data['cd_praca'])
        
    
#    actions_str = ''
    
    if(text == 'Alerta'):
        update.message.reply_text(first_name + ', você poderá verificar esses alertas: ')
#        try:
#            update.message.reply_text(first_name + ', você poderá verificar esses alertas: ' + str(id_func))
#        except Exception as e:
#            print(e)
#            
        
    else:
        update.message.reply_text('Sua opção não foi reconhecida. Por favor, tente novamente.', reply_markup=opt_markup)
        return ADMIN_OPTION
    
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
    
def cancel(bot, update):
    user = update.message.from_user    
    update.message.reply_text('Tchau %S!', user.first_name)
    return ConversationHandler.END

def main():
    
    updater = Updater('425927387:AAGOwjYib6TjshazA5uibYF_EnpWMRHo5YM')
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(            
            entry_points = [CommandHandler('start', start)], 
            
            states = {
                    CONTACT: [MessageHandler(Filters.contact, contact)],
                    
#                    ADMIN_OPTION: [CallbackQueryHandler(client_option)],
                    
                    ADMIN_OPTION: [RegexHandler('^(Alerta)$', func_option, pass_user_data=True),
                                   RegexHandler('^(Outros)$', func_option, pass_user_data=True)]
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