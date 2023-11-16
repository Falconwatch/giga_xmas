import dotenv
import os
import telebot
import configparser
import logging
import argparse

from db_manager import DBManager
from llm_handler import Giga

dotenv.load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
assert(os.environ["GIGACHAT_CREDENTIALS"])


parser = argparse.ArgumentParser()
parser.add_argument("--log", help="type of logs")
args = parser.parse_args()

if args.log:
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(filename='debug.log', encoding='utf-8', level=numeric_level)

class DtaasHelper:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('conf/config.conf')
        self.db_path = config['DEFAULT']['db_path']
        self.prompt_template = config['DEFAULT']['prompt_template']
        self.error_response = config['DEFAULT']['error_response']
        self.greeting_response = config['DEFAULT']['greeting']
        self.sys_message = config['DEFAULT']['sys_message']
        # Инициализируем бота
        self.bot = telebot.TeleBot(BOT_TOKEN)
        # Инициализируем гигачат
        self.llmh = Giga(self.prompt_template, self.sys_message)

        self.db = DBManager(self.db_path)

        def gen_markup():
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(telebot.types.InlineKeyboardButton("👍", callback_data="like"),
                                    telebot.types.InlineKeyboardButton("👎", callback_data="dislike"),
                                    telebot.types.InlineKeyboardButton("🔁", callback_data="rewrite"))
            return markup

        @self.bot.message_handler(commands=["start"])
        def start(message, res=False):
            response = self.greeting_response
            self.bot.send_message(
                message.chat.id, response, parse_mode="markdown")
            self.db.log_message(message, response)


        @self.bot.message_handler(content_types=["text"])
        def handle_text(message):
            response = self.error_response
            try:
                response = self.llmh.call(message.text)
            except Exception as e:
                logging.error("Can not get a response from LLM" + str(e))
            self.bot.reply_to(message, response, reply_markup=gen_markup())
            #self.db.log_message(message, response)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if call.data=="like":
                like = 1
                self.bot.answer_callback_query(call.id, "Спасибо за оценку!")
            elif call.data=="dislike":
                like = -1
                self.bot.answer_callback_query(call.id, "Спасибо за оценку!")
            elif call.data=="rewrite":
                like = -1
                response = self.error_response
                try:
                    response = self.llmh.call(call.message.reply_to_message.text)
                except Exception as e:
                    pass
                self.bot.edit_message_text(response, 
                                           chat_id=call.message.chat.id, message_id=call.message.id, 
                                           reply_markup=gen_markup())
            else:
                like = 0
            self.db.log_like(call.message.id, call.message.chat.id, like)
            
            

    def run(self):
        print('bot is pooling...')
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    # Запускаем бота
    bot = DtaasHelper()
    bot.run()
