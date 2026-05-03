from database import execute, fetchone, fetchall
from models.user import User

class PointsTransaction:
    TYPE_CHECKIN = 'checkin'
    TYPE_EXCHANGE_BALANCE = 'exchange_balance'
    TYPE_EXCHANGE_POSTS = 'exchange_posts'
    TYPE_INVITE_REWARD = 'invite_reward'
    TYPE_SHARE_REWARD = 'share_reward'
    TYPE_ADMIN_GRANT = 'admin_grant'
    TYPE_ADMIN_DEDUCT = 'admin_deduct'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.points = kwargs.get('points')
        self.transaction_type = kwargs.get('transaction_type')
        self.description = kwargs.get('description')
        self.related_id = kwargs.get('related_id')
        self.created_at = kwargs.get('created_at')
        self._user = None
    
    @staticmethod
    def create(user_id, points, transaction_type, description=None, related_id=None):
        trans_id = execute(
            '''INSERT INTO points_transactions (user_id, points, transaction_type, description, related_id)
               VALUES (%s, %s, %s, %s, %s) RETURNING id''',
            (user_id, points, transaction_type, description, related_id)
        )
        return PointsTransaction.get_by_id(trans_id)
    
    @staticmethod
    def get_by_id(trans_id):
        row = fetchone('SELECT * FROM points_transactions WHERE id = %s', (trans_id,))
        return PointsTransaction(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM points_transactions 
               WHERE user_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return [PointsTransaction(**row) for row in rows]
    
    @staticmethod
    def count_by_user(user_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM points_transactions WHERE user_id = %s',
            (user_id,)
        )
        return row['count'] if row else 0
    
    def get_user(self):
        if self._user is None:
            self._user = User.get_by_id(self.user_id)
        return self._user
    
    def get_type_name(self):
        type_names = {
            self.TYPE_CHECKIN: '每日签到',
            self.TYPE_EXCHANGE_BALANCE: '兑换余额',
            self.TYPE_EXCHANGE_POSTS: '兑换发布额度',
            self.TYPE_INVITE_REWARD: '邀请奖励',
            self.TYPE_SHARE_REWARD: '分享奖励',
            self.TYPE_ADMIN_GRANT: '管理员发放',
            self.TYPE_ADMIN_DEDUCT: '管理员扣除'
        }
        return type_names.get(self.transaction_type, self.transaction_type)
    
    def to_dict(self, include_user=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'points': self.points,
            'transaction_type': self.transaction_type,
            'type_name': self.get_type_name(),
            'description': self.description,
            'related_id': self.related_id,
            'created_at': self.created_at
        }
        
        if include_user:
            user = self.get_user()
            if user:
                data['user'] = {
                    'id': user.id,
                    'username': user.username
                }
        
        return data
