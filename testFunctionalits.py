#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 11:21:51 2017

@author: diego
"""

from telegram import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)
import pyodbc 
import datetime

""""""
updater = Updater('425927387:AAGOwjYib6TjshazA5uibYF_EnpWMRHo5YM')
dp = updater.dispatcher
jb = updater.job_queue
""""""

CONN_STR = ()

CONTACT = range(4)
ADMIN_OPTION = range(4)
ADMIN_ACTION = range(4)


#keyboard = [[InlineKeyboardButton("Monitorar Alerta", callback_data='Alerta'), InlineKeyboardButton(
#        "Outros", callback_data='Outros')]]
#opt_markup = InlineKeyboardMarkup(keyboard)

reply_keyboard = [['Alerta'], ['Outros']]
opt_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

functionary_data = dict()
client_data = dict()
agenda = dict()

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
        functionary_data['id_funcionario'] = row.id_funcionario
        functionary_data['no_funcionario'] = row.no_funcionario
        
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
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text('Opcao escolhida: ' + text, reply_markup=ReplyKeyboardRemove())
    
    first_name = (functionary_data['no_funcionario']).partition(' ')[0]    
    id_func = functionary_data['id_funcionario']
    
    query = "select * from UsuarioSistema where id_funcionario = " + str(id_func)
    row = consult_db(query)
    
    if(row is 'None'):
        print('consult is empty')
    else:
        """
        user data storage
        """
        functionary_data['cd_praca'] = row.cd_praca
        functionary_data['sg_departamento'] = row.sg_departamento
        
        """"""""""""""""""""""""""""""
        if(functionary_data['sg_departamento'] is 'None'):
            update.message.reply_text(first_name + 
                                      ', verifiquei que você não está em um departamento. Por favor, peça ao pessoal do administrativo que te cadastre.')
            update.message.reply_text('Para me desativar digite: /desativar')            
        else:
            update.message.reply_text(first_name + ', verifiquei que você é do departamento de ' + functionary_data['sg_departamento'])
        
    
    if(text == 'Alerta'):
#        update.message.reply_text('Você poderá monitorar esses alertas: ')
        
        try:
            query = "select * from alt_alerta_departamento dp inner join alt_alerta al on al.id_alerta = dp.id_alerta and al.st_alerta = 'A' where dp.cd_praca = '" + functionary_data[
                    'cd_praca'] + "' and dp.sg_departamento = '" + functionary_data['sg_departamento'] + "'"
            row = consult_db_list(query)
            
            if(row is 'None'):
                update.message.reply_text('Desculpe ' + first_name + '! Não há alertas cadastrados para o seu departamento.')
            else:
                actions = dict()
                for i in row:
                   actions[i.id_alerta] = i.ds_alerta
                   
                button_list = [InlineKeyboardButton(v, callback_data=k) for k, v in actions.items()]                
                reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))                
                update.message.reply_text('Você poderá monitorar esses alertas:\n', reply_markup=reply_markup)                
                return ADMIN_ACTION
            
        except Exception as e:
            print(e)
    else:
        update.message.reply_text('Sua opção não foi reconhecida. Por favor, tente novamente.', reply_markup=opt_markup)
        return ADMIN_OPTION
    
def callback_minute(bot, job):
    now = datetime.datetime.now().time()
    start = datetime.time(now.hour, now.minute)
    
    query = "select no_sp from alt_conteudo_alerta c inner join alt_alerta a on a.id_conteudo = c.id_conteudo where a.id_alerta = " + str(functionary_data['id_alerta'])
    
    for t in functionary_data['agenda']:
        row = consult_db(query)
        break
#        if(start == t):
#            print("Entrou callback_minute")    
#        else:
#            print("Não entrou callback_minute")
    
    alert = consult_db_list(str(row.no_sp))
    print(alert)

                
    
def func_action(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="Selected option: %s" % query.data,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    
    functionary_data['id_alerta'] = query.data    
    row = consult_db_list("p_alt_select_agenda_por_dia")
    
    if(row is 'None'):
        print('Sem alertas')
    else:
        try:
            functionary_data['agenda'] = []
            
            for a in row:
                if(str(a.id_alerta) == str(functionary_data['id_alerta'])):
                    (functionary_data['agenda']).append(a.hr_envio)
                    
            # Add job to queue
#            update.message.reply_text('Ok. Agora você irá recever os alertas por aqui!')
            jb.run_repeating(callback_minute, interval=60, first=0)
    
        except (IndexError, ValueError) as e:
            print(e)
    
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
    
def cancel(bot, update):
    user = update.message.from_user    
    update.message.reply_text('Tchau %S!', user.first_name)
    return ConversationHandler.END

def main():        
    conv_handler = ConversationHandler(            
            entry_points = [CommandHandler('start', start)], 
            
            states = {
                    CONTACT: [MessageHandler(Filters.contact, contact)],                   
                    
                    ADMIN_OPTION: [RegexHandler('^(Alerta)$', func_option, pass_user_data=True),
                                   RegexHandler('^(Outros)$', func_option, pass_user_data=True)],                    
            },     
                    
            fallbacks = [CommandHandler('cancel', cancel)]
    )
    
    dp.add_handler(CallbackQueryHandler(func_action))
    
    # Add commands to the dispatcher
    dp.add_handler(conv_handler)
    
    # Finish
    dp.add_handler(CommandHandler('desativar', cancel))
    
    # By default poll_interval = 0, timeout = 10
    updater.start_polling()
    
    # Stops execution with ctrl+c
    updater.idle()
    
if __name__ == '__main__':
    main()