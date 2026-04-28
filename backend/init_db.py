import psycopg2
from config import Config

def column_exists(cursor, table_name, column_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        )
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def init_database():
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        database=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        )
    """)
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        if not column_exists(cursor, 'posts', 'views_count'):
            cursor.execute('ALTER TABLE posts ADD COLUMN views_count INTEGER DEFAULT 0')
            print('Added missing column: posts.views_count')
        
        if not column_exists(cursor, 'posts', 'is_pinned'):
            cursor.execute('ALTER TABLE posts ADD COLUMN is_pinned INTEGER DEFAULT 0')
            print('Added missing column: posts.is_pinned')
        
        if not column_exists(cursor, 'posts', 'pinned_at'):
            cursor.execute('ALTER TABLE posts ADD COLUMN pinned_at TIMESTAMP')
            print('Added missing column: posts.pinned_at')
        
        if not column_exists(cursor, 'posts', 'pin_expires_at'):
            cursor.execute('ALTER TABLE posts ADD COLUMN pin_expires_at TIMESTAMP')
            print('Added missing column: posts.pin_expires_at')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_views_count ON posts(views_count)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_is_pinned ON posts(is_pinned)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_pinned_at ON posts(pinned_at)')
        conn.commit()
        conn.close()
        return
    
    cursor.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            avatar VARCHAR(255),
            level VARCHAR(50) DEFAULT 'bronze',
            posts_count INTEGER DEFAULT 0,
            balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            view_permission VARCHAR(50) DEFAULT 'all',
            images TEXT,
            is_task INTEGER DEFAULT 0,
            views_count INTEGER DEFAULT 0,
            is_pinned INTEGER DEFAULT 0,
            pinned_at TIMESTAMP,
            pin_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE comments (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_views_count ON posts(views_count)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    print('Database initialized successfully!')
