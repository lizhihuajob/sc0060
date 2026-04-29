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
        
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'comments'
            )
        ''')
        comments_table_exists = cursor.fetchone()[0]
        
        if not comments_table_exists:
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)')
            print('Created table: comments')
        
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'favorites'
            )
        ''')
        favorites_table_exists = cursor.fetchone()[0]
        
        if not favorites_table_exists:
            cursor.execute('''
                CREATE TABLE favorites (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    post_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                    UNIQUE(user_id, post_id)
                )
            ''')
            cursor.execute('CREATE INDEX idx_favorites_user_id ON favorites(user_id)')
            cursor.execute('CREATE INDEX idx_favorites_post_id ON favorites(post_id)')
            print('Created table: favorites')
        
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'follows'
            )
        ''')
        follows_table_exists = cursor.fetchone()[0]
        
        if not follows_table_exists:
            cursor.execute('''
                CREATE TABLE follows (
                    id SERIAL PRIMARY KEY,
                    follower_id INTEGER NOT NULL,
                    following_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (following_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(follower_id, following_id)
                )
            ''')
            cursor.execute('CREATE INDEX idx_follows_follower_id ON follows(follower_id)')
            cursor.execute('CREATE INDEX idx_follows_following_id ON follows(following_id)')
            print('Created table: follows')
        
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'likes'
            )
        ''')
        likes_table_exists = cursor.fetchone()[0]
        
        if not likes_table_exists:
            cursor.execute('''
                CREATE TABLE likes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    post_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                    UNIQUE(user_id, post_id)
                )
            ''')
            cursor.execute('CREATE INDEX idx_likes_user_id ON likes(user_id)')
            cursor.execute('CREATE INDEX idx_likes_post_id ON likes(post_id)')
            print('Created table: likes')
        
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'notifications'
            )
        ''')
        notifications_table_exists = cursor.fetchone()[0]
        
        if not notifications_table_exists:
            cursor.execute('''
                CREATE TABLE notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    data TEXT DEFAULT '{}',
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('CREATE INDEX idx_notifications_user_id ON notifications(user_id)')
            cursor.execute('CREATE INDEX idx_notifications_is_read ON notifications(is_read)')
            cursor.execute('CREATE INDEX idx_notifications_created_at ON notifications(created_at)')
            print('Created table: notifications')
        
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
    
    cursor.execute('''
        CREATE TABLE favorites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            UNIQUE(user_id, post_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE follows (
            id SERIAL PRIMARY KEY,
            follower_id INTEGER NOT NULL,
            following_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (following_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(follower_id, following_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE likes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            UNIQUE(user_id, post_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            data TEXT DEFAULT '{}',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_views_count ON posts(views_count)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)')
    cursor.execute('CREATE INDEX idx_favorites_user_id ON favorites(user_id)')
    cursor.execute('CREATE INDEX idx_favorites_post_id ON favorites(post_id)')
    cursor.execute('CREATE INDEX idx_follows_follower_id ON follows(follower_id)')
    cursor.execute('CREATE INDEX idx_follows_following_id ON follows(following_id)')
    cursor.execute('CREATE INDEX idx_likes_user_id ON likes(user_id)')
    cursor.execute('CREATE INDEX idx_likes_post_id ON likes(post_id)')
    cursor.execute('CREATE INDEX idx_notifications_user_id ON notifications(user_id)')
    cursor.execute('CREATE INDEX idx_notifications_is_read ON notifications(is_read)')
    cursor.execute('CREATE INDEX idx_notifications_created_at ON notifications(created_at)')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    print('Database initialized successfully!')
