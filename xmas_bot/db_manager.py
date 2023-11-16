import sqlite3
from datetime import datetime
from db import DB


class DBManager:
    def __init__(self, db_path):
        self.db = DB(db_path)
    
    def log_message(self, message, response):
        self.db.save_message(message.message_id, message.from_user.id, message.chat.id,
                             message.text, response)
        self.db.flush()

    def log_like(self, message_id, chat_id, like):
        self.db.update_like(message_id, chat_id, like)
        self.db.flush()
