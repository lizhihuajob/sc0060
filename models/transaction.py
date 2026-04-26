from database import execute, fetchone, fetchall
from models.user import User

class Transaction:
    TYPE_RECHARGE = 'recharge'
    TYPE_UPGRADE = 'upgrade'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.amount = kwargs.get('amount')
        self.transaction_type = kwargs.get('transaction_type')
        self.description = kwargs.get('description')
        self.created_at = kwargs.get('created_at')
        self._user = None
    
    @staticmethod
    def create(user_id, amount, transaction_type, description=None):
        trans_id = execute(
            '''INSERT INTO transactions (user_id, amount, transaction_type, description)
               VALUES (%s, %s, %s, %s) RETURNING id''',
            (user_id, amount, transaction_type, description)
        )
        return Transaction.get_by_id(trans_id)
    
    @staticmethod
    def get_by_id(trans_id):
        row = fetchone('SELECT * FROM transactions WHERE id = %s', (trans_id,))
        return Transaction(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM transactions WHERE user_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return [Transaction(**row) for row in rows]
    
    def get_user(self):
        if self._user is None:
            self._user = User.get_by_id(self.user_id)
        return self._user
    
    def get_type_name(self):
        if self.transaction_type == self.TYPE_RECHARGE:
            return '充值'
        elif self.transaction_type == self.TYPE_UPGRADE:
            return '升级'
        return self.transaction_type
    
    def to_dict(self, include_user=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'type_name': self.get_type_name(),
            'description': self.description,
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
