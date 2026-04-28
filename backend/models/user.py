from werkzeug.security import generate_password_hash, check_password_hash
from database import execute, fetchone, fetchall
from config import Config

class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.email = kwargs.get('email')
        self.avatar = kwargs.get('avatar')
        self.level = kwargs.get('level', 'bronze')
        self.posts_count = kwargs.get('posts_count', 0)
        self.balance = kwargs.get('balance', 0)
        self.created_at = kwargs.get('created_at')
    
    @staticmethod
    def create(username, password, email=None):
        hashed_password = generate_password_hash(password)
        user_id = execute(
            'INSERT INTO users (username, password, email) VALUES (%s, %s, %s) RETURNING id',
            (username, hashed_password, email)
        )
        return User.get_by_id(user_id)
    
    @staticmethod
    def get_by_id(user_id):
        row = fetchone('SELECT * FROM users WHERE id = %s', (user_id,))
        return User(**row) if row else None
    
    @staticmethod
    def get_by_username(username):
        row = fetchone('SELECT * FROM users WHERE username = %s', (username,))
        return User(**row) if row else None
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_level_info(self):
        return Config.USER_LEVELS.get(self.level, Config.USER_LEVELS['bronze'])
    
    def get_posts_limit(self):
        return self.get_level_info()['posts_limit']
    
    def can_post(self):
        return self.posts_count < self.get_posts_limit()
    
    def increment_posts_count(self):
        execute(
            'UPDATE users SET posts_count = posts_count + 1 WHERE id = %s',
            (self.id,)
        )
        self.posts_count += 1
    
    def get_available_posts(self):
        return self.get_posts_limit() - self.posts_count
    
    def upgrade_level(self, new_level):
        if new_level not in Config.USER_LEVELS:
            return False
        
        current_level_order = list(Config.USER_LEVELS.keys())
        current_index = current_level_order.index(self.level)
        new_index = current_level_order.index(new_level)
        
        if new_index <= current_index:
            return False
        
        level_info = Config.USER_LEVELS[new_level]
        if self.balance < level_info['price']:
            return False
        
        self.balance -= level_info['price']
        execute(
            'UPDATE users SET level = %s, balance = %s WHERE id = %s',
            (new_level, self.balance, self.id)
        )
        self.level = new_level
        return True
    
    def add_balance(self, amount):
        new_balance = self.balance + amount
        if new_balance < 0:
            return False
        
        self.balance = new_balance
        execute(
            'UPDATE users SET balance = %s WHERE id = %s',
            (self.balance, self.id)
        )
        return True
    
    def get_next_level(self):
        level_order = list(Config.USER_LEVELS.keys())
        current_index = level_order.index(self.level)
        
        if current_index < len(level_order) - 1:
            next_level_key = level_order[current_index + 1]
            return {
                'key': next_level_key,
                'info': Config.USER_LEVELS[next_level_key]
            }
        return None
    
    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            return False
        
        hashed_password = generate_password_hash(new_password)
        execute(
            'UPDATE users SET password = %s WHERE id = %s',
            (hashed_password, self.id)
        )
        self.password = hashed_password
        return True
    
    def update_avatar(self, avatar_filename):
        execute(
            'UPDATE users SET avatar = %s WHERE id = %s',
            (avatar_filename, self.id)
        )
        self.avatar = avatar_filename
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'level': self.level,
            'level_name': self.get_level_info()['name'],
            'posts_count': self.posts_count,
            'posts_limit': self.get_posts_limit(),
            'balance': self.balance,
            'created_at': self.created_at
        }
