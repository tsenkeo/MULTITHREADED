#!/usr/bin/python3
# -*- coding: utf-8 -*-

from telebot import *
from telebot import types, util
from threading import Thread
import time
from colorama import Fore


class Sending_messages_to_users:
    def __init__(self,
        json, 
        text: 'текст сообщения', 
        database: 'подключение к базе данных', 
        src_image = None):

        self._json = json
        self._text = text
        self._src_image = src_image

        cursor = database.cursor()
        cursor.execute(f'''SELECT "ID" FROM "USERS";''')
        self._list_id = cursor.fetchall()
        if self._list_id == []:
            cursor.close()
            raise MyException('Нет пользоватлей в базе')
        elif self._list_id != []:
            cursor.close()

        for i in range(0, len(self._json['bots'])):
            token = self._json['bots'][i]['token']
            
            if src_image is None:
                print(Fore.GREEN + f'Запуск потока для рассылки ')
                sending = Thread(target=self.send, args=(token, ), daemon=True).start()
                time.sleep(2)

            else:
                print(Fore.GREEN + f'Запуск потока для рассылки')
                sending = Thread(target=self.send, args=(token, True), daemon=True).start()
                time.sleep(2)


    def send(self, token, with_image: bool = False):

        delivered: 'сколько доставлено сообщений' = 0

        bot = telebot.TeleBot(token, parse_mode="MarkdownV2")

        for i in range(0, len(self._list_id)):
            try:
                id = self._list_id[i]['ID']
                if with_image == False:
                    bot.send_message(chat_id=id, text=self._text)
                    delivered += 1

                elif with_image == True:
                    image = open(self._src_image, 'rb')
                    bot.send_photo(chat_id=id, photo=image,
                    caption=self._text)
                    image.close()
                    delivered += 1
                    time.sleep(3)
            except telebot.apihelper.ApiException:
                pass
        
        print(Fore.RED + f'Доставлено сообщений: {delivered}')

        
