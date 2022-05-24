from config import BOT_TOKEN
from multiprocessing import *
import telebot, sqlite3
import schedule, time
from telebot import types
bot = telebot.TeleBot(BOT_TOKEN)
worker_dict = {}
workers = []
class IncrementCounter:
    
    def __init__(self):
        self._value = 0
    
    def new_value(self):
        self._value += 1
        return self._value
counter1 = IncrementCounter()
counter2 = IncrementCounter()
counter3 = IncrementCounter()
class Worker:
    def __init__(self, name):
        self.name = name
        self.id = None
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

def db_table_val(user_id: int, user_name: str, everyday:int):
	cursor.execute('INSERT INTO worker (user_id, user_name, everyday) VALUES (?, ?, ?)', (user_id, user_name, everyday))
	conn.commit()
def db_table_val_q(text: str, user_id: int):
	cursor.execute('INSERT INTO quest (text, user_id) VALUES (?, ?)', (text, user_id))
	conn.commit()
def everyday_sms():
    cursor.execute(f'SELECT * from worker')
    a = cursor.fetchall()
    bot.send_message(1134632256, 'Ежедневный отчет:')
    for i in a:
        cursor.execute(f"Update worker set everyday = 0 where id = {i[0]}")
        conn.commit()
        bot.send_message(1134632256, f'{i[2]} Выполнил {i[3]} Заданий(е)')
def everyweek_sms():
    cursor.execute(f'SELECT * from worker')
    a = cursor.fetchall()
    bot.send_message(1134632256, 'Еженедельный отчет:')
    for i in a:
        cursor.execute(f"Update worker set eweryweek = 0 where id = {i[0]}")
        conn.commit()
        bot.send_message(1134632256, f'{i[2]} Выполнил {i[3]} Заданий(е)')
class MarkUser:
    btn4 = types.KeyboardButton('Мои задания')
    btn5 = types.KeyboardButton('Завершить задание')
    btn7 = types.KeyboardButton("Проверить меня в бд")
    glav_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    glav_markup.add(btn4, btn5, btn7)
class MarkAdmin:
    glav_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("Задать задачу")
    btn2 = types.KeyboardButton("Все работники")
    btn3 = types.KeyboardButton('+ работник')
    btn6 = types.KeyboardButton("Удалить работника")
    
    glav_markup.add(btn1, btn2, btn3, btn6)
@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.id == 1134632256:

        bot.send_message(1134632256, 'Здравствуйте, Админ, ваша админ панель:', reply_markup=MarkAdmin.glav_markup)
    else:
        bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup=MarkUser.glav_markup)
@bot.message_handler(content_types=["text"])
def core(message):  
    if message.text == 'Проверить меня в бд':
        cursor.execute(f"SELECT * FROM worker WHERE user_id = {message.chat.id}")
        if cursor.fetchone() == None:
            bot.send_message(message.chat.id, 'Вас нет в нашей базе данных!')
        else:
            cursor.execute(f"SELECT * FROM worker WHERE user_id = {message.chat.id}")
            a = cursor.fetchone()
            bot.send_message(message.chat.id, f'{a[2]}, Вы есть в нашей базе данных')
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
        
        user = worker_dict[chat_id]
        user.id = id
        db_table_val(user_id=id, user_name=user.name, everyday=0)
        
        bot.send_message(message.chat.id,f'Вы добавили работника {user.name}')
    
      
    except Exception as e:
        bot.reply_to(message, e)
def core2( message):
    try:
        
        cursor.execute(f'SELECT * FROM worker where id = {message.text}')
        global o
        o = cursor.fetchone()
        bot.send_message(o[1], 'Для тебя готовится задание')
        msg = bot.send_message(1134632256, f'Какое задание мы дадим "{o[2]}"', reply_markup=MarkAdmin.glav_markup)
        bot.register_next_step_handler(msg, quest)
    except Exception as e:
        bot.send_message(1134632256, e)
def final_quest(message):
    try:
        quest_id = message.text
        cursor.execute(f'SELECT * FROM quest where id = {quest_id}')
        global dok_quest
        dok_quest = cursor.fetchone()
        msg = bot.send_message(message.chat.id, f'Пожалуйста, скиньте фотодоказательства проделанной работы задания"{dok_quest[1]}"))', reply_markup=MarkUser.glav_markup)
        bot.register_next_step_handler(msg, dok_photos)
    except Exception as e:
        bot.send_message(1134632256, e)
def agree(message):
    if message.text == 'Да' and message.chat.id == 1134632256:
        try:
            bot.send_message(1134632256, f"задание '{dok_quest[1]}' засчитано!", reply_markup=MarkAdmin.glav_markup)

            bot.send_message(dok_quest[2], f"Ваше задание '{dok_quest[1]}' засчитано! Поздравляем! Всего вы решили {counter1.new_value()} заданий")
            cursor.execute(f"Update worker set everyday = {counter2.new_value()} where user_id = {dok_quest[2]}")
            cursor.execute(f"Update worker set everyweek = {counter3.new_value()} where user_id = {dok_quest[2]}")
            cursor.execute(f'DELETE from quest where id = {dok_quest[0]}')
            conn.commit()
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
        bot.send_message(message.chat.id,f'Работник "{worker[2]} был удален"', reply_markup=MarkAdmin.glav_markup)
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


def start_process():
    p1 = Process(target=start_schedule, args=()).start()

def start_schedule():
   schedule.every().day.at("00:00").do(everyday_sms)
   schedule.every(1).weeks.do(everyweek_sms)
   while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    start_process()
    bot.polling(none_stop=True)