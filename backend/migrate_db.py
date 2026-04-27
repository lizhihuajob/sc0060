import psycopg2
from config import Config

def migrate_database():
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        database=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'avatar'
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(255)")
        print("Added 'avatar' column to users table")
    
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'posts' AND column_name = 'views_count'
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE posts ADD COLUMN views_count INTEGER DEFAULT 0")
        print("Added 'views_count' column to posts table")
    
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'comments'
        )
    """)
    if not cursor.fetchone()[0]:
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
        print("Created 'comments' table")
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)')
        print("Created indexes for comments table")
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_views_count ON posts(views_count)')
    print("Created index idx_posts_views_count")
    
    conn.commit()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
