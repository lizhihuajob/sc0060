import psycopg2
from config import Config

def migrate_admin():
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        database=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    print('开始迁移数据库...')
    
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'posts' AND column_name = 'status'
        )
    ''')
    status_column_exists = cursor.fetchone()[0]
    
    if not status_column_exists:
        print('添加 posts.status 列...')
        cursor.execute("ALTER TABLE posts ADD COLUMN status VARCHAR(50) DEFAULT 'active'")
    else:
        print('posts.status 列已存在')
    
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'posts' AND column_name = 'hidden_by'
        )
    ''')
    hidden_by_exists = cursor.fetchone()[0]
    
    if not hidden_by_exists:
        print('添加 posts.hidden_by 列...')
        cursor.execute('ALTER TABLE posts ADD COLUMN hidden_by INTEGER')
    else:
        print('posts.hidden_by 列已存在')
    
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'posts' AND column_name = 'hidden_at'
        )
    ''')
    hidden_at_exists = cursor.fetchone()[0]
    
    if not hidden_at_exists:
        print('添加 posts.hidden_at 列...')
        cursor.execute('ALTER TABLE posts ADD COLUMN hidden_at TIMESTAMP')
    else:
        print('posts.hidden_at 列已存在')
    
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'posts' AND column_name = 'hidden_reason'
        )
    ''')
    hidden_reason_exists = cursor.fetchone()[0]
    
    if not hidden_reason_exists:
        print('添加 posts.hidden_reason 列...')
        cursor.execute('ALTER TABLE posts ADD COLUMN hidden_reason TEXT')
    else:
        print('posts.hidden_reason 列已存在')
    
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'admins'
        )
    ''')
    admins_table_exists = cursor.fetchone()[0]
    
    if not admins_table_exists:
        print('创建 admins 表...')
        cursor.execute('''
            CREATE TABLE admins (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                role VARCHAR(50) DEFAULT 'admin',
                is_active INTEGER DEFAULT 1,
                last_login_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username)')
        print('admins 表创建成功')
    else:
        print('admins 表已存在')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)')
    print('创建索引完成')
    
    conn.commit()
    conn.close()
    print('数据库迁移完成！')

if __name__ == '__main__':
    migrate_admin()
