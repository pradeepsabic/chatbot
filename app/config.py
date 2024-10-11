
# Manage your configuration and secrets such as API keysimport os
import os
api_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = api_key

DATABASE_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\MSSQLSERVER02;"  # Or your server name
    "DATABASE=Chatbot;"
    "UID=pradeep;"
    "PWD=pradeep;"
)