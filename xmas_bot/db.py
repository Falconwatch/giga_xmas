import sqlite3
from datetime import datetime


class DB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table_if_exists()

    def __del__(self):
        self.conn.close()

    def create_table_if_exists(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages(
                                                                    message_id INTEGER PRIMARY KEY,
                                                                    user_id INTEGER NOT NULL,
                                                                    chat_id INTEGER NOT NULL,
                                                                    message TEXT,
                                                                    response TEXT, 
                                                                    time t_i DEFAULT (strftime('%d/%m/%Y %H:%M:%S')),
                                                                    like INTEGER
                                                                    )
                                """
                            )

    def save_message(self,
                     message_id:int, from_user_id:int, chat_id:int,
                     message_text:str, response_text:str, like:int = 0
                     ):
        current_dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cursor.execute("INSERT INTO  messages VALUES(?, ?, ?, ?, ?, ?, ?)", (
        message_id, from_user_id, chat_id, message_text, response_text, current_dt, like))

    def update_like(self, message_id, chat_id, like_status):
        sql_update_query = """Update messages set like = ? where message_id = ? and chat_id = ?"""
        data = (like_status,  message_id, chat_id,)
        self.cursor.execute(sql_update_query, data)

    def flush(self):
        self.conn.commit()
