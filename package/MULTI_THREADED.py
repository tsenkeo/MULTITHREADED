#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import datetime, pytz
from telebot import *
from telebot import types, util

from threading import Thread
import time, json
from .SEND import Sending_messages_to_users

from colorama import Fore


def today():
    '''Получение даты и времени'''
    today = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')
    return today


class Multithreaded:

    def __init__(self, polling: bool = False):

        print(Fore.RED + f'Привет! Чтобы изменить настройки ботов-прокладок'\
            ' (например, добавить или удалить бот, изменить администратора, ссылку куда пользователям переходить)'\
            ' отредактируй файл config.json')

        self._json = json.load(open('config.json', 'r', encoding='utf-8'))
        self._polling = polling

        if __name__ != '__main__':
            global db
            with sqlite3.connect('package/BASE.db', check_same_thread=False) as database:
                database.row_factory = self.dict_factory 
                db = database
                self.create_database(database)

            print(Fore.GREEN + 'База данных поключена')

        
        for i in range(0, len(self._json['bots'])):
            try:
                th = i + 1
                print(Fore.GREEN + f'Запуск потока {th}')
                token = self._json['bots'][i]['token']
                redirect = self._json['bots'][i]['redirect']
                Thread(target=self.all_func, args=(token, redirect)).start()
                time.sleep(2)
            except Exception:
                break
       

    def all_func(self, token, redirect):
        admin_id = self._json['admin_id']
        json = self._json

        bot = telebot.TeleBot(token, parse_mode="MarkdownV2", threaded=False) 
        
        while True:
            @bot.message_handler(commands=['start'])
            def wait_command(message):

                parse_mode = '*Пожалуйста, подождите\.\.\.*⏳'
                send = bot.send_message(message.chat.id, parse_mode)
            
                bot.delete_message(message.chat.id, message.message_id)
                    
                if self.check_user(id=message.from_user.id) is True:
                    pass
                elif self.check_user(id=message.from_user.id) is False:
                    self.add_user(message.from_user.id)

                parse_mode = '*Чтобы продолжить нажмите на кнопку ниже*' 
                keyboard = types.InlineKeyboardMarkup()
                url_btn = types.InlineKeyboardButton(text='➡️Нажмите здесь⬅️', url=redirect)
                keyboard.add(url_btn)

                bot.send_message(message.chat.id, parse_mode, reply_markup=keyboard) 
                bot.delete_message(message.chat.id, send.id)    

            @bot.message_handler(commands=['send'])
            def mailing_command(message):
                if message.from_user.id == admin_id:
                    parse_mode = f'*Отправь отформатированный текст* [MarkdownV2](https://core.telegram.org/bots/api#markdownv2-style), *который нужно отправить пользователям*\.\nДля передачи символов форматирования экранруй их с помощью обратной косой черты\.\nЕсли хочешь разослать пользователям изображение с текстом \- отправь его как файл с описанием\.'
                    k = types.ForceReply()
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, text=parse_mode,
                                    reply_markup=k)


            @bot.message_handler(content_types=['text'])
            def text(message):
                if message.reply_to_message.text == f'Отправь отформатированный текст MarkdownV2, который нужно отправить пользователям.\nДля передачи символов форматирования экранруй их с помощью обратной косой черты.\nЕсли хочешь разослать пользователям изображение с текстом - отправь его как файл с описанием.' and message.from_user.id == admin_id:
                    m = message.json
                    text = m['text']

                    bot.delete_message(message.chat.id, message.message_id)
                    bot.delete_message(message.chat.id, message.reply_to_message.id)
                    
                    keyboard_mailing = types.InlineKeyboardMarkup()
                    button_information = types.InlineKeyboardButton(text='Отправить пользователям?', callback_data=' ')
                    callback_button_send_mailing = types.InlineKeyboardButton(text='✅ Да', callback_data='send_mailing')
                    callback_button_send_myself = types.InlineKeyboardButton(text='Отправить самому себе', callback_data='send_to_myself')
                    keyboard_mailing.add(button_information)
                    keyboard_mailing.add(callback_button_send_mailing)
                    keyboard_mailing.add(callback_button_send_myself)
                    
                    parse_mode = f'{text}'
                    bot.send_message(message.chat.id, text=parse_mode, reply_markup=keyboard_mailing)


            @bot.callback_query_handler(func=lambda call: True)
            def calling_button(call):
                if call.data == 'send_mailing':
                    if call.message.photo:
                        text = call.message.caption                   
                        src = 'package/image.jpg'
                        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                        Sending_messages_to_users(json=json, text=text, database=db, src_image=src)
    
                    else:
                        m = call.message.json
                        text = m['text']
                        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                        Sending_messages_to_users(json=json, text=text, database=db)

                elif call.data == 'send_to_myself':
                    if call.message.photo:
                        text = call.message.caption                   
                        src = 'package/image.jpg'
                        image = open(src, 'rb')
                        bot.send_photo(chat_id=call.message.chat.id, photo=image,
                        caption=text)
                        image.close()
                    else:
                        m = call.message.json
                        text = m['text']        
                        bot.send_message(call.message.chat.id, text=text)      
                    
            
            
            @bot.message_handler(content_types=['document'])
            def photo(message):
 
                if message.reply_to_message.text == f'Отправь отформатированный текст MarkdownV2, который нужно отправить пользователям.\nДля передачи символов форматирования экранруй их с помощью обратной косой черты.\nЕсли хочешь разослать пользователям изображение с текстом - отправь его как файл с описанием.' and message.from_user.id == admin_id:
                    text = message.caption
                    image_id = message.document.file_id

                    file_info = bot.get_file(image_id)
                    src = 'package/image.jpg'
                    download_file = bot.download_file(file_info.file_path)
                        
                    saving_in_dir = open(src, 'wb')
                    saving_in_dir.write(download_file)
                    saving_in_dir.close()

                    bot.delete_message(message.chat.id, message.message_id)
                    bot.delete_message(message.chat.id, message.reply_to_message.id)

                    image = open(src, 'rb')

                    keyboard_mailing = types.InlineKeyboardMarkup()
                    button_information = types.InlineKeyboardButton(text='Отправить пользователям?', callback_data=' ')
                    callback_button_send_mailing = types.InlineKeyboardButton(text='✅ Да', callback_data='send_mailing')
                    callback_button_send_myself = types.InlineKeyboardButton(text='Отправить самому себе', callback_data='send_to_myself')
                    keyboard_mailing.add(button_information)
                    keyboard_mailing.add(callback_button_send_mailing)
                    keyboard_mailing.add(callback_button_send_myself)
                    
                    parse_mode = f'{text}'
                    bot.send_photo(chat_id=message.chat.id, photo=image, caption=parse_mode, reply_markup=keyboard_mailing)

                    image.close()

            if self._polling == True:
                try:
                    bot.infinity_polling() #polling(none_stop=True) #
                except Exception as e: 
                    print(e)
                    time.sleep(5)    



    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_database(self, database: 'подключение к базе данных'):
        '''
        Создание таблицы в базе данных
        '''
        cursor = database.cursor()
        cursor.executescript(f'''CREATE TABLE IF NOT EXISTS "USERS"("ID" INTEGER NOT NULL,                                                                 
                                                                    "LAUNCH_DATE" TEXT);
                            ''')
        database.commit()
        cursor.close()

    def add_user(self, id):
        cursor = db.cursor()
        insert_data = (id, today())
        cursor.execute('INSERT INTO "USERS" VALUES(?, ?);', insert_data)
        db.commit()
        cursor.close()
        return True

    def check_user(self, id):
        '''ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ НА НАЛИЧИЕ В БАЗЕ'''
        cursor = db.cursor()
        cursor.execute(f'SELECT "ID" FROM "USERS" WHERE "ID" = "{id}";')
        data = cursor.fetchone()
        if data is None:
            cursor.close()
            return False
        elif id == data['ID']:
            cursor.close()
            return True