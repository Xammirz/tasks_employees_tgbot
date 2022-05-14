
from config import BOT_TOKEN
import telebot, sqlite3
from telebot import types
bot = telebot.TeleBot(BOT_TOKEN)
worker_dict = {}
workers = []
class Worker:
    def __init__(self, name):
        self.name = name
        self.id = None
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
def db_table_val(user_id: int, user_name: str):
	cursor.execute('INSERT INTO worker (user_id, user_name) VALUES (?, ?)', (user_id, user_name))
	conn.commit()
def db_table_val_q(text: str, user_id: int):
	cursor.execute('INSERT INTO quest (text, user_id) VALUES (?, ?)', (text, user_id))
	conn.commit()
@bot.message_handler(commands=["start"])
def start(message):
    global glav_markup
    glav_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("Задать задачу")
    btn2 = types.KeyboardButton("Все работники")
    btn3 = types.KeyboardButton('+ работник')
    btn4 = types.KeyboardButton('Мои задания')
    btn5 = types.KeyboardButton('Завершить задание')
    btn6 = types.KeyboardButton("Удалить работника")
    if message.chat.id == 1134632256:
        glav_markup.add(btn1, btn2, btn3, btn6)
        
        bot.send_message(1134632256, 'Здравствуйте, Админ, ваша админ панель:', reply_markup=glav_markup)
    else:
        glav_markup.add(btn4, btn5)
        bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup=glav_markup)
@bot.message_handler(content_types=["text"])
def core(message):  
    if message.text == 'Удалить работника' and message.chat.id == 1134632256:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        try:
            cursor.execute('SELECT * FROM worker')
            n = cursor.fetchall()
            for row in n:
                markup.add(types.KeyboardButton(row[0]))
                bot.send_message(1134632256, f'id:{row[0]}\nИмя:{row[2]}')
        except Exception as e:
            bot.send_message(1134632256, e)
        msg = bot.send_message(1134632256, 'Выберите кого удалить', reply_markup=markup)
        bot.register_next_step_handler(msg,delete_worker)
    if message.text == 'Мои задания':
        try:
            cursor.execute(f'SELECT * FROM quest where user_id = {message.chat.id}')
            quest_texts = cursor.fetchall()      
            bot.send_message(message.chat.id, f'Вот ваши задания:')     
            for row in quest_texts:
                
                bot.send_message(message.chat.id, f'{row[0]}: {row[1]}')
        except Exception as e:
            bot.send_message(1134632256, e)
    if message.text == 'Завершить задание':
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        try:
            cursor.execute(f'SELECT * FROM quest where user_id = {message.chat.id}')
            quest_texts = cursor.fetchall()
            for row in quest_texts:
                markup.add(types.KeyboardButton(row[0]))
                bot.send_message(message.chat.id, f'{row[0]}: {row[1]}') 
            msg = bot.send_message(message.chat.id, 'Какое задание вы хотите завершить?', reply_markup=markup)
            bot.register_next_step_handler(msg,final_quest)
        except Exception as e:
            bot.send_message(1134632256, e)
    if (message.text == 'Задать задачу') and message.chat.id == 1134632256:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        try:
            cursor.execute('SELECT * FROM worker')
            n = cursor.fetchall()
            for row in n:
                markup.add(types.KeyboardButton(row[0]))
                bot.send_message(1134632256, f'id:{row[0]}\nИмя:{row[2]}')
            msg = bot.send_message(1134632256, 'Выберите кому задать задачу', reply_markup=markup)
            bot.register_next_step_handler(msg,core2)
        except Exception as e:
            bot.send_message(1134632256, e)
    if (message.text == 'Все работники') and message.chat.id == 1134632256:
        try:
            bot.send_message(1134632256, 'Все работники:')
            cursor.execute('SELECT * FROM worker')
            n = cursor.fetchall()
            for row in n:
                bot.send_message(1134632256, f'id:{row[0]}\nИмя:{row[2]}')
        except Exception as e:
            bot.send_message(1134632256, e)
    if (message.text == '+ работник') and message.chat.id == 1134632256:
        msg = bot.reply_to(message, """Имя работника?""")
        bot.register_next_step_handler(msg,worker_name)
def worker_name(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = Worker(name)
        worker_dict[chat_id] = user
        msg = bot.reply_to(message, 'Ид работника?')
        bot.register_next_step_handler(msg, worker_id)
    except Exception as e:
        bot.reply_to(message, 'oooops')
def worker_id(message):
    try:
        chat_id = message.chat.id
        id = message.text
        if not id.isdigit():
            msg = bot.reply_to(message, 'Ид бывает цифрами')
            bot.register_next_step_handler(msg, worker_id)
            return
        if len(id) == 10:
            user = worker_dict[chat_id]
            user.id = id
            db_table_val(user_id=id, user_name=user.name)
            bot.send_message(message.chat.id,f'Вы добавили работника {user.name}')
        else:
            bot.send_message(message.chat.id,f'Проверьте верность ид!')
    except Exception as e:
        bot.reply_to(message, e)
def core2( message):
    try:
        cursor.execute(f'SELECT * FROM worker where id = {message.text}')
        global o
        o = cursor.fetchone()
        bot.send_message(o[1], 'Для тебя готовится задание')
        msg = bot.send_message(1134632256, f'Какое задание мы дадим "{o[2]}"')
        bot.register_next_step_handler(msg, quest)
    except Exception as e:
        bot.send_message(1134632256, e)
def final_quest(message):
    try:
        quest_id = message.text
        cursor.execute(f'SELECT * FROM quest where id = {quest_id}')
        global dok_quest
        dok_quest = cursor.fetchone()
        msg = bot.send_message(message.chat.id, f'Пожалуйста, скиньте фотодоказательства проделанной работы задания"{dok_quest[1]}"))')
        bot.register_next_step_handler(msg, dok_photos)
    except Exception as e:
        bot.send_message(1134632256, e)
def agree(message):
    if message.text == 'Да' and message.chat.id == 1134632256:
        try:
            bot.send_message(dok_quest[2], f"Ваше задание '{dok_quest[1]}' засчитано! Поздравляем")
            cursor.execute(f'DELETE from quest where id = {dok_quest[0]}')
        except Exception as e:
            bot.send_message(1134632256, e)
    if message.text == 'Нет' and message.chat.id == 1134632256: 
        bot.send_message(dok_quest[2], f"Ваше задание '{dok_quest[1]}' не засчитано! Попробуйте еще раз!")
def quest(message):
    quest_text = message.text  
    db_table_val_q(text=quest_text, user_id=o[1])
    bot.send_message(o[1],f'Для тебя пришло задание от админа!!\n\n\n{quest_text}')
def delete_worker(message):
    try:
        cursor.execute(f'SELECT * FROM worker where id = {message.text}')
        worker = cursor.fetchone()
        bot.send_message(message.chat.id,f'Работник "{worker[2]} был удален"')
        cursor.execute(f'DELETE from worker where id = {message.text}')
        conn.commit()
    except Exception as e:
        bot.send_message(1134632256, e)
@bot.message_handler(content_types=["photos"])
def dok_photos(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)
    bot.copy_message(chat_id=1134632256, from_chat_id=message.chat.id, message_id=message.id)
    msg = bot.send_message(1134632256, f'Задание "{dok_quest[1]}" присылается, засчитывать задание?', reply_markup=markup)
    bot.register_next_step_handler(msg, agree)
bot.polling(none_stop=False)