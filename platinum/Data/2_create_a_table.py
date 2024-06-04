import sqlite3

conn = sqlite3.connect('data/binar_data_science.db')
print("Opened database successfully")

conn.execute('''CREATE TABLE users (username varchar(255), email varchar(255));''')
print("Table created successfully")

conn.close()