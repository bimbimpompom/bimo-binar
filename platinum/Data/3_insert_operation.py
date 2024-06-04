import sqlite3

conn = sqlite3.connect('data/binar_data_science.db')
print("Opened database successfully")

conn.execute("INSERT INTO users (username, email) VALUES ('binaria', 'binaria@binar.com')")
conn.execute("INSERT INTO users VALUES ('bintang', 'bintang@binar.com')")

conn.commit()
print("Records created successfully")
conn.close()