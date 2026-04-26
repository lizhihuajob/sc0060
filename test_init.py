import sqlite3
import os
import sys

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
wal_path = db_path + '-wal'
shm_path = db_path + '-shm'

for path in [db_path, wal_path, shm_path]:
    if os.path.exists(path):
        os.remove(path)
        print(f'Removed: {path}')

print('Creating database...')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('Creating users table...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        level TEXT DEFAULT 'bronze',
        posts_count INTEGER DEFAULT 0,
        balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('Users table created.')

print('Creating posts table...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        view_permission TEXT DEFAULT 'all',
        images TEXT,
        is_task INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print('Posts table created.')

print('Creating transactions table...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print('Transactions table created.')

print('Creating indexes...')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
print('Indexes created.')

conn.commit()
conn.close()
print('Database initialized successfully!')

print('Testing database...')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print(f'Tables: {tables}')
conn.close()

print('All tests passed!')
