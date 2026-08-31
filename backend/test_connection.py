from db import get_db_connection


connection = get_db_connection()

print("Database connection successful!")

connection.close()