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
        self.is_banned = kwargs.get('is_banned', 0)
        self.banned_at = kwargs.get('banned_at')
        self.banned_by = kwargs.get('banned_by')
        self.ban_reason = kwargs.get('ban_reason')
        self.created_at = kwargs.get('created_at')
        self._banned_by_admin = None
    
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
    
    @staticmethod
    def get_all_for_admin(limit=20, offset=0, level=None, keyword=None):
        base_conditions = ['1=1']
        params = []
        
        if level:
            base_conditions.append('level = %s')
            params.append(level)
        
        if keyword:
            base_conditions.append('(username ILIKE %s OR email ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param])
        
        where_clause = ' AND '.join(base_conditions)
        
        query = f'''SELECT * FROM users WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [User(**row) for row in rows]
    
    @staticmethod
    def count_for_admin(level=None, keyword=None):
        base_conditions = ['1=1']
        params = []
        
        if level:
            base_conditions.append('level = %s')
            params.append(level)
        
        if keyword:
            base_conditions.append('(username ILIKE %s OR email ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param])
        
        where_clause = ' AND '.join(base_conditions)
        
        query = f'''SELECT COUNT(*) as count FROM users WHERE {where_clause}'''
        
        row = fetchone(query, params)
        return row['count'] if row else 0
    
    @staticmethod
    def get_total_recharge():
        from models.transaction import Transaction
        row = fetchone(
            '''SELECT SUM(amount) as total FROM transactions 
               WHERE transaction_type = %s AND amount > 0''',
            (Transaction.TYPE_RECHARGE,)
        )
        return row['total'] if row and row['total'] else 0
    
    def get_transactions_summary(self):
        from models.transaction import Transaction
        transactions = Transaction.get_by_user(self.id, limit=100)
        
        total_recharge = 0
        total_spent = 0
        
        for t in transactions:
            if t.transaction_type == Transaction.TYPE_RECHARGE and t.amount > 0:
                total_recharge += t.amount
            elif t.amount < 0:
                total_spent += abs(t.amount)
        
        return {
            'total_recharge': total_recharge,
            'total_spent': total_spent,
            'transaction_count': len(transactions)
        }
    
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
        if amount <= 0:
            return False
        
        self.balance += amount
        execute(
            'UPDATE users SET balance = balance + %s WHERE id = %s',
            (amount, self.id)
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
    
    def ban(self, admin_id, reason=None):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE users SET is_banned = %s, banned_at = %s, banned_by = %s, ban_reason = %s 
               WHERE id = %s''',
            (1, now, admin_id, reason, self.id)
        )
        self.is_banned = 1
        self.banned_at = now
        self.banned_by = admin_id
        self.ban_reason = reason
        return True
    
    def unban(self):
        execute(
            '''UPDATE users SET is_banned = %s, banned_at = %s, banned_by = %s, ban_reason = %s 
               WHERE id = %s''',
            (0, None, None, None, self.id)
        )
        self.is_banned = 0
        self.banned_at = None
        self.banned_by = None
        self.ban_reason = None
        return True
    
    def is_banned_user(self):
        return self.is_banned == 1
    
    def get_banned_by_admin(self):
        if self._banned_by_admin is None and self.banned_by:
            from models.admin import Admin
            self._banned_by_admin = Admin.get_by_id(self.banned_by)
        return self._banned_by_admin
    
    def to_dict(self, include_transactions_summary=False, include_admin_info=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'level': self.level,
            'level_name': self.get_level_info()['name'],
            'posts_count': self.posts_count,
            'posts_limit': self.get_posts_limit(),
            'balance': self.balance,
            'is_banned': self.is_banned_user(),
            'created_at': self.created_at
        }
        
        if include_admin_info:
            data['banned_at'] = self.banned_at
            data['banned_by'] = self.banned_by
            data['ban_reason'] = self.ban_reason
            
            banned_admin = self.get_banned_by_admin()
            if banned_admin:
                data['banned_by_admin'] = {
                    'id': banned_admin.id,
                    'username': banned_admin.username
                }
        
        if include_transactions_summary:
            transactions_summary = self.get_transactions_summary()
            data.update(transactions_summary)
        
        return data
