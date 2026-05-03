from database import execute, fetchone, fetchall
from datetime import datetime
from models.user import User

class InviteRecord:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.inviter_id = kwargs.get('inviter_id')
        self.invited_user_id = kwargs.get('invited_user_id')
        self.reward_amount = kwargs.get('reward_amount', 0)
        self.reward_claimed = kwargs.get('reward_claimed', 0)
        self.claimed_at = kwargs.get('claimed_at')
        self.created_at = kwargs.get('created_at')
        self._inviter = None
        self._invited_user = None
    
    @staticmethod
    def create(inviter_id, invited_user_id, reward_amount=0):
        record_id = execute(
            '''INSERT INTO invite_records (inviter_id, invited_user_id, reward_amount)
               VALUES (%s, %s, %s) RETURNING id''',
            (inviter_id, invited_user_id, reward_amount)
        )
        return InviteRecord.get_by_id(record_id)
    
    @staticmethod
    def get_by_id(record_id):
        row = fetchone('SELECT * FROM invite_records WHERE id = %s', (record_id,))
        return InviteRecord(**row) if row else None
    
    @staticmethod
    def get_by_invited_user(invited_user_id):
        row = fetchone(
            'SELECT * FROM invite_records WHERE invited_user_id = %s',
            (invited_user_id,)
        )
        return InviteRecord(**row) if row else None
    
    @staticmethod
    def get_by_inviter(inviter_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM invite_records 
               WHERE inviter_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (inviter_id, limit, offset)
        )
        return [InviteRecord(**row) for row in rows]
    
    @staticmethod
    def count_by_inviter(inviter_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM invite_records WHERE inviter_id = %s',
            (inviter_id,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def count_unclaimed_by_inviter(inviter_id):
        row = fetchone(
            '''SELECT COUNT(*) as count FROM invite_records 
               WHERE inviter_id = %s AND reward_claimed = 0''',
            (inviter_id,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def get_total_reward_by_inviter(inviter_id):
        row = fetchone(
            '''SELECT SUM(reward_amount) as total FROM invite_records 
               WHERE inviter_id = %s''',
            (inviter_id,)
        )
        return row['total'] if row and row['total'] else 0
    
    def claim_reward(self):
        if self.reward_claimed == 1:
            return False
        
        now = datetime.now()
        execute(
            '''UPDATE invite_records 
               SET reward_claimed = 1, claimed_at = %s 
               WHERE id = %s''',
            (now, self.id)
        )
        self.reward_claimed = 1
        self.claimed_at = now
        return True
    
    def get_inviter(self):
        if self._inviter is None:
            self._inviter = User.get_by_id(self.inviter_id)
        return self._inviter
    
    def get_invited_user(self):
        if self._invited_user is None:
            self._invited_user = User.get_by_id(self.invited_user_id)
        return self._invited_user
    
    def to_dict(self, include_inviter=False, include_invited_user=False):
        data = {
            'id': self.id,
            'inviter_id': self.inviter_id,
            'invited_user_id': self.invited_user_id,
            'reward_amount': self.reward_amount,
            'reward_claimed': self.reward_claimed == 1,
            'claimed_at': self.claimed_at,
            'created_at': self.created_at
        }
        
        if include_inviter:
            inviter = self.get_inviter()
            if inviter:
                data['inviter'] = {
                    'id': inviter.id,
                    'username': inviter.username,
                    'avatar': inviter.avatar
                }
        
        if include_invited_user:
            invited_user = self.get_invited_user()
            if invited_user:
                data['invited_user'] = {
                    'id': invited_user.id,
                    'username': invited_user.username,
                    'avatar': invited_user.avatar,
                    'created_at': invited_user.created_at
                }
        
        return data
