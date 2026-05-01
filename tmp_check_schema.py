import sqlite3, os
path = os.path.join(os.getcwd(), 'sgp.db')
print('DB path', path)
print('exists', os.path.exists(path))
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute('PRAGMA table_info(users)')
cols = c.fetchall()
print('users columns:')
for col in cols:
    print(col)
conn.close()
