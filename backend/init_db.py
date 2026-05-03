import psycopg2
from config import Config

def table_exists(cursor, table_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def column_exists(cursor, table_name, column_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        )
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def create_table_if_not_exists(cursor, table_name, create_sql):
    if not table_exists(cursor, table_name):
        cursor.execute(create_sql)
        print(f'Created table: {table_name}')
    else:
        print(f'Table already exists: {table_name}')

def init_database():
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        database=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    
    print('Starting database initialization...')
    
    create_table_if_not_exists(cursor, 'admins', '''
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
    
    create_table_if_not_exists(cursor, 'tags', '''
        CREATE TABLE tags (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            color VARCHAR(20) DEFAULT '#0071e3',
            icon VARCHAR(50),
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    create_table_if_not_exists(cursor, 'users', '''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            avatar VARCHAR(255),
            level VARCHAR(50) DEFAULT 'bronze',
            posts_count INTEGER DEFAULT 0,
            balance REAL DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            banned_at TIMESTAMP,
            banned_by INTEGER,
            ban_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (banned_by) REFERENCES admins (id)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'posts', '''
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
            status VARCHAR(50) DEFAULT 'active',
            hidden_by INTEGER,
            hidden_at TIMESTAMP,
            hidden_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'transactions', '''
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
    
    create_table_if_not_exists(cursor, 'comments', '''
        CREATE TABLE comments (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parent_id INTEGER,
            reply_to_user_id INTEGER,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE,
            FOREIGN KEY (reply_to_user_id) REFERENCES users (id)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'favorites', '''
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
    
    create_table_if_not_exists(cursor, 'edit_logs', '''
        CREATE TABLE edit_logs (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title_before TEXT,
            content_before TEXT,
            view_permission_before VARCHAR(50),
            is_task_before INTEGER DEFAULT 0,
            title_after TEXT,
            content_after TEXT,
            view_permission_after VARCHAR(50),
            is_task_after INTEGER DEFAULT 0,
            edit_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'post_tags', '''
        CREATE TABLE post_tags (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
            UNIQUE(post_id, tag_id)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'reports', '''
        CREATE TABLE reports (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            target_type VARCHAR(50) NOT NULL,
            target_id INTEGER NOT NULL,
            reason VARCHAR(50) NOT NULL,
            reason_detail TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            handled_by INTEGER,
            handled_at TIMESTAMP,
            handled_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (handled_by) REFERENCES admins (id)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'announcements', '''
        CREATE TABLE announcements (
            id SERIAL PRIMARY KEY,
            admin_id INTEGER NOT NULL,
            title VARCHAR(500) NOT NULL,
            content TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            pinned_at TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active',
            publish_at TIMESTAMP,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES admins (id)
        )
    ''')
    
    print('Checking for missing columns...')
    
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
    
    if not column_exists(cursor, 'posts', 'status'):
        cursor.execute("ALTER TABLE posts ADD COLUMN status VARCHAR(50) DEFAULT 'active'")
        print('Added missing column: posts.status')
    
    if not column_exists(cursor, 'posts', 'hidden_by'):
        cursor.execute('ALTER TABLE posts ADD COLUMN hidden_by INTEGER')
        print('Added missing column: posts.hidden_by')
    
    if not column_exists(cursor, 'posts', 'hidden_at'):
        cursor.execute('ALTER TABLE posts ADD COLUMN hidden_at TIMESTAMP')
        print('Added missing column: posts.hidden_at')
    
    if not column_exists(cursor, 'posts', 'hidden_reason'):
        cursor.execute('ALTER TABLE posts ADD COLUMN hidden_reason TEXT')
        print('Added missing column: posts.hidden_reason')
    
    if not column_exists(cursor, 'posts', 'updated_at'):
        cursor.execute('ALTER TABLE posts ADD COLUMN updated_at TIMESTAMP')
        print('Added missing column: posts.updated_at')
    
    if not column_exists(cursor, 'users', 'is_banned'):
        cursor.execute('ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0')
        print('Added missing column: users.is_banned')
    
    if not column_exists(cursor, 'users', 'banned_at'):
        cursor.execute('ALTER TABLE users ADD COLUMN banned_at TIMESTAMP')
        print('Added missing column: users.banned_at')
    
    if not column_exists(cursor, 'users', 'banned_by'):
        cursor.execute('ALTER TABLE users ADD COLUMN banned_by INTEGER')
        print('Added missing column: users.banned_by')
    
    if not column_exists(cursor, 'users', 'ban_reason'):
        cursor.execute('ALTER TABLE users ADD COLUMN ban_reason TEXT')
        print('Added missing column: users.ban_reason')
    
    if not column_exists(cursor, 'comments', 'parent_id'):
        cursor.execute('ALTER TABLE comments ADD COLUMN parent_id INTEGER')
        print('Added missing column: comments.parent_id')
    
    if not column_exists(cursor, 'comments', 'reply_to_user_id'):
        cursor.execute('ALTER TABLE comments ADD COLUMN reply_to_user_id INTEGER')
        print('Added missing column: comments.reply_to_user_id')
    
    if not column_exists(cursor, 'users', 'points'):
        cursor.execute('ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0')
        print('Added missing column: users.points')
    
    if not column_exists(cursor, 'users', 'invite_code'):
        cursor.execute('ALTER TABLE users ADD COLUMN invite_code VARCHAR(20) UNIQUE')
        print('Added missing column: users.invite_code')
    
    if not column_exists(cursor, 'users', 'invited_by'):
        cursor.execute('ALTER TABLE users ADD COLUMN invited_by INTEGER')
        print('Added missing column: users.invited_by')
    
    if not column_exists(cursor, 'users', 'last_checkin_date'):
        cursor.execute('ALTER TABLE users ADD COLUMN last_checkin_date DATE')
        print('Added missing column: users.last_checkin_date')
    
    if not column_exists(cursor, 'users', 'continuous_checkin_days'):
        cursor.execute('ALTER TABLE users ADD COLUMN continuous_checkin_days INTEGER DEFAULT 0')
        print('Added missing column: users.continuous_checkin_days')
    
    create_table_if_not_exists(cursor, 'checkin_records', '''
        CREATE TABLE checkin_records (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            checkin_date DATE NOT NULL,
            points_earned INTEGER DEFAULT 0,
            continuous_days INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, checkin_date)
        )
    ''')
    
    create_table_if_not_exists(cursor, 'points_transactions', '''
        CREATE TABLE points_transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            points INTEGER NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            description TEXT,
            related_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    create_table_if_not_exists(cursor, 'invite_records', '''
        CREATE TABLE invite_records (
            id SERIAL PRIMARY KEY,
            inviter_id INTEGER NOT NULL,
            invited_user_id INTEGER NOT NULL,
            reward_amount REAL DEFAULT 0,
            reward_claimed INTEGER DEFAULT 0,
            claimed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inviter_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (invited_user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(invited_user_id)
        )
    ''')
    
    print('Creating indexes...')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_is_active ON tags(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_sort_order ON tags(sort_order)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_views_count ON posts(views_count)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_is_pinned ON posts(is_pinned)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_pinned_at ON posts(pinned_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_post_id ON favorites(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_edit_logs_post_id ON edit_logs(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_edit_logs_user_id ON edit_logs(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_edit_logs_created_at ON edit_logs(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_tags_post_id ON post_tags(post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_tags_tag_id ON post_tags(tag_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_target ON reports(target_type, target_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_announcements_admin_id ON announcements(admin_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_announcements_is_pinned ON announcements(is_pinned)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_announcements_status ON announcements(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_announcements_created_at ON announcements(created_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_checkin_records_user_id ON checkin_records(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_checkin_records_checkin_date ON checkin_records(checkin_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_points_transactions_user_id ON points_transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_points_transactions_created_at ON points_transactions(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_invite_records_inviter_id ON invite_records(inviter_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_invite_records_invited_user_id ON invite_records(invited_user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_invite_code ON users(invite_code)')
    
    print('Indexes created/verified')
    
    print('Initializing default tags...')
    
    default_tags = [
        {'name': '紧急', 'slug': 'urgent', 'description': '需要紧急处理的事项', 'color': '#FF3B30', 'sort_order': 1},
        {'name': '招聘', 'slug': 'recruitment', 'description': '招聘信息相关', 'color': '#FF9500', 'sort_order': 2},
        {'name': '活动', 'slug': 'activity', 'description': '活动通知相关', 'color': '#30D158', 'sort_order': 3},
        {'name': '公告', 'slug': 'announcement', 'description': '正式公告通知', 'color': '#007AFF', 'sort_order': 4},
        {'name': '求助', 'slug': 'help', 'description': '寻求帮助的请求', 'color': '#AF52DE', 'sort_order': 5},
        {'name': '分享', 'slug': 'share', 'description': '经验或资源分享', 'color': '#5AC8FA', 'sort_order': 6},
    ]
    
    for tag in default_tags:
        cursor.execute('''
            INSERT INTO tags (name, slug, description, color, sort_order, is_active, created_at, updated_at)
            SELECT %s, %s, %s, %s, %s, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM tags WHERE slug = %s)
        ''', (tag['name'], tag['slug'], tag['description'], tag['color'], tag['sort_order'], tag['slug']))
        if cursor.rowcount > 0:
            print(f'Added default tag: {tag["name"]}')
    
    conn.commit()
    conn.close()
    print('Database initialization completed!')

if __name__ == '__main__':
    init_database()
    print('Database initialized successfully!')
