import telebot
from datetime import datetime, timedelta
import random
#  import requests
#  from bs4 import BeautifulSoup

TOKEN = "YOUR_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)
stats = {} # Статистика


f = open('facts.txt', 'r', encoding='UTF-8')
facts = f.read().split('\n')
f.close()

# поговорки
d = open('thinks.txt', 'r', encoding='UTF-8')
think = d.read().split('\n')
d.close()

bad_words = ['word']



@bot.message_handler(commands=['ban'])
def ban_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if is_user_admin(chat_id, user_id):
        try:
            user_to_ban = message.reply_to_message.from_user.id
            bot.kick_chat_member(chat_id, user_to_ban)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был успешно забанен!")
        except Exception as e:
            bot.reply_to(message, "Ой, похоже произошла ошибка")
    else:
        bot.reply_to(message, "Эта команда доступна только для админов!")


@bot.message_handler(commands=['unban'])
def unban_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if is_user_admin(chat_id, user_id):
        try:
            user_to_unban = message.reply_to_message.from_user.id
            bot.unban_chat_member(chat_id, user_to_unban)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был успешно разбанен!")
        except Exception as e:
            bot.reply_to(message, "Ой, похоже произошла ошибка")
    else:
        bot.reply_to(message, "Эта команда доступна только для админов!")


def is_user_admin(chat_id, user_id):
    chat_member = bot.get_chat_member(chat_id, user_id)
    return chat_member.status == "administrator" or chat_member.status == "creator"



@bot.message_handler(commands=['mute'])
def mute_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        command = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите время мьюта в часах.")
        return
    try:
        mute_duration = int(command)
    except ValueError:
        bot.reply_to(message, "Некорректное время. Укажите время мьюта в часах целым числом.")
        return
    if is_user_admin(chat_id, user_id):
        try:
            user_to_mute = message.reply_to_message.from_user.id
            mute_duration = datetime.now() + timedelta(hours=mute_duration)
            bot.restrict_chat_member(chat_id, user_to_mute, until_date=mute_duration)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username}"
                                  f" был успешно замьючен на {command} час!")
        except Exception as e:
            bot.reply_to(message, "Ой, похоже произошла ошибка")
    else:
        bot.reply_to(message, "Эта команда доступна только для админов!")



@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if is_user_admin(chat_id, user_id):
        try:
            user_to_unmute = message.reply_to_message.from_user.id
            bot.restrict_chat_member(chat_id, user_to_unmute, can_send_messages=True, can_send_media_messages=True,
                                     can_send_other_messages=True, can_add_web_page_previews=True)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username}"
                                  f" был успешно размьючен!")
        except Exception as e:
            bot.reply_to(message, "Ой, похоже произошла ошибка")
    else:
        bot.reply_to(message, "Эта команда доступна только для админов!")


@bot.message_handler(commands=['selfstats'])
def user_stats(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    if chat_id not in stats:
        bot.reply_to(message, "Статистика чата пуста.")
    else:
        if user_id not in stats[chat_id]['users']:
            bot.reply_to(message, "Вы еще не отправляли сообщений в этом чате.")
        else:
            user_messages = stats[chat_id]['users'][user_id]['messages']
            total_messages = stats[chat_id]['total_messages']
            percentage = round(user_messages / total_messages * 100, 2)
            bot.reply_to(message, f"Статистика для пользователя @{username}:\nВсего сообщений: {user_messages}\nПроцент"
                                  f" от общего количества сообщений: {percentage}%")


@bot.message_handler(commands=['stats'])
def chat_stats(message):
    chat_id = message.chat.id
    if chat_id not in stats:
        bot.reply_to(message, "Статистика чата пуста.")
    else:
        total_messages = stats[chat_id]['total_messages']
        unique_users = len(stats[chat_id]['users'])
        bot.reply_to(message, f"Статистика чата:\nВсего сообщений: {total_messages}\nУникальных пользователей: {unique_users}")


@bot.message_handler(commands=['fact'])
def fact(message):
    answer = random.choice(facts)
    bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['thinks'])
def thinks(message):
    answer = random.choice(think)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in bad_words))
def handle_bad_words(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    mute_duration = datetime.now() + timedelta(hours=1)

    # Delete the message
    bot.delete_message(chat_id, message.message_id)

    # Mute the user for 1 hour
    bot.restrict_chat_member(chat_id, user_id, until_date=mute_duration)
    bot.reply_to(message, f"Вы сказали нехорошее слово из черного списка! Пользователь {message.from_user.username} "
                          f"стоит в углу на 1 час!")


@bot.message_handler(commands=['cube'])
def cube(message):
    bot.send_message(message.chat.id, "🎲")

@bot.message_handler(commands=["GOIDA", "goida"])
def goida_start(message):
    try:
        goida_num = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Неверно введена команда. Пример: /goidа 10")
        return
    for i in range(int(goida_num)):
        bot.send_message(message.chat.id, "ГОЙДА!!!!")
    bot.send_message(message.chat.id, "Гойда кончилась((")

@bot.message_handler(commands=["return"])
def return_text(message):
    try:
        command_parts = message.text.split(maxsplit=2)
        many_return = int(command_parts[1])
        text_to_return = command_parts[2]
    except IndexError:
        bot.reply_to(message, "Неверно введена команда. Пример: /return <кол-во повторений> <текст>")
        return
    for i in range(int(many_return)):
        bot.send_message(message.chat.id, text_to_return)
    bot.send_message(message.chat.id, "Конец повторений")




if __name__ == '__main__':
    bot.polling(none_stop=True)