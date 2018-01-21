import sqlite3
import telebot
import logging
import time
from telebot import types

CONN = sqlite3.connect('spoiler.db', check_same_thread=False)
LOGGER = telebot.logger
BOT  = telebot.TeleBot(token='', skip_pending=True)

def main():
    """Create the database if not exists
    """
    print('Ejecutado')
    cursor = CONN.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS `groups` ( `group_id` NUMERIC, `users` NUMERIC NOT NULL,\
     PRIMARY KEY(`group_id`))')

    cursor.execute('CREATE TABLE IF NOT EXISTS "mods" ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, \
    `user_id` NUMERIC NOT NULL, `group_id` NUMERIC NOT NULL, FOREIGN KEY(`group_id`) REFERENCES groups )')

    cursor.execute('CREATE TABLE IF NOT EXISTS `messages` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT,\
    `group_id` NUMERIC NOT NULL, `user_id` NUMERIC NOT NULL, `sender_id` NUMERIC NOT NULL,\
    `sender` TEXT, `text` TEXT NOT NULL, `date` NUMERIC NOT NULL, FOREIGN KEY(`group_id`) REFERENCES groups,\
    FOREIGN KEY(`user_id`) REFERENCES mods )')
    cursor.close()
    CONN.commit()
    telebot.logger.setLevel(logging.INFO)
    BOT.polling(none_stop=False)

@BOT.message_handler(commands=['spoiler'])
def spoiler_handler(msg: types.Message):
    update(msg.chat.id)
    if msg.reply_to_message:
        spoiler_reply(msg)
    else:
        print('Es un mensaje')

@BOT.message_handler(func=lambda m: True)
def pruebas(msg):
    BOT.send_message(msg.chat.id, 'HOLI')

def spoiler_reply(msg: types.Message):
    mod = BOT.get_chat_member(msg.chat.id, msg.from_user.id)
    cursor = CONN.cursor()
    cursor.execute('SELECT COUNT(user_id) FROM mods WHERE user_id = {} AND group_id = {}'
                   .format(mod.user.id, msg.chat.id))
    is_mod = cursor.fetchone()[0]
    print('MOD: ', is_mod, ' STATUS: ',  mod.status)
    if is_mod or mod.status in  ['creator', 'administrator']:
        print('TAMO DENTRO')
        reply = msg.reply_to_message

        cursor.execute('INSERT INTO messages (group_id, user_id, sender_id, sender, text, date) \
        VALUES({}, {}, {}, "{}", "{}", {})'\
        .format(msg.chat.id, mod.user.id, reply.from_user.id, reply.from_user.username, reply.text, time.time()))
        cursor.close()
        CONN.commit()
        BOT.delete_message(msg.chat.id, reply.message_id)
        BOT.delete_message(msg.chat.id, msg.message_id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        itembtn1 = types.InlineKeyboardButton(text='OPEN️', callback_data= str(reply.message_id))
        markup.add(itembtn1)
        if len(msg.text.split()) > 1:
            BOT.send_message(chat_id=msg.chat.id, text='‼️ Esto es un spoiler, clic en el botón para verlo‼️\n%s'%msg.text[8:].strip(), reply_markup=markup)
        else:
            BOT.send_message(chat_id=msg.chat.id, text='‼️ Esto es un spoiler, clic en el botón para verlo‼️', reply_markup=markup)

def update(chat_id):
    users = BOT.get_chat_members_count(chat_id)
    cursor = CONN.cursor()
    cursor.execute('INSERT OR REPLACE INTO groups (group_id, users) VALUES ({}, {})'
                   .format(chat_id, users))
    cursor.close()
    CONN.commit()

if __name__ == '__main__':
    main()
