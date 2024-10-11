import pyodbc
from datetime import datetime
from app.config import DATABASE_CONNECTION_STRING

class DBManager:
    def __init__(self):
        self.conn = pyodbc.connect(DATABASE_CONNECTION_STRING)
        self.cursor = self.conn.cursor()

    def save_query_to_db(self, query: str, intent: str,sentiment:str):
        timestamp = datetime.now()
        self.cursor.execute(
            "INSERT INTO ChatbotQueries (Query, Intent, sentiment, Timestamp) VALUES (?, ?, ?,?)", 
            (query, intent, sentiment, timestamp)
        )
        self.conn.commit()

    def get_recent_queries(self):
        # SQL query to get the last 100 queries and intents
        self.cursor.execute('''
            SELECT TOP 100 Query, Intent
            FROM ChatbotQueries
            ORDER BY Timestamp DESC
        ''')
        rows = self.cursor.fetchall()
        return [{"query": row[0], "intent": row[1]} for row in rows]

    def close_connection(self):
        self.conn.close()