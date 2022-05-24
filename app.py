from bot import bot,start_process

if __name__ == '__main__':
    start_process()
    bot.polling(none_stop=True)