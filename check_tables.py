import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'smru_%' ORDER BY name")
print('Existing tables in database:')
for row in cursor.fetchall():
    table_name = row[0]
    print(f'  {table_name}')

conn.close()
