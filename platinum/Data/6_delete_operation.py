import sqlite3

conn = sqlite3.connect('data/binar_data_science.db')
print("Opened database successfully")
print()

conn.execute("DELETE FROM users where username = 'bintang';")
conn.commit()

print("List of Users:")
cursor = conn.execute("SELECT * FROM users;")
for row in cursor:
    print(row)
    
print()
print("Operation done successfully")
conn.close