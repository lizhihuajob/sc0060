from database import execute, fetchone, fetchall
from datetime import date, datetime, timedelta
from models.user import User

class CheckinRecord:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.checkin_date = kwargs.get('checkin_date')
        self.points_earned = kwargs.get('points_earned', 0)
        self.continuous_days = kwargs.get('continuous_days', 0)
        self.created_at = kwargs.get('created_at')
        self._user = None
    
    @staticmethod
    def create(user_id, checkin_date=None, points_earned=0, continuous_days=0):
        if checkin_date is None:
            checkin_date = date.today()
        
        record_id = execute(
            '''INSERT INTO checkin_records (user_id, checkin_date, points_earned, continuous_days)
               VALUES (%s, %s, %s, %s) RETURNING id''',
            (user_id, checkin_date, points_earned, continuous_days)
        )
        return CheckinRecord.get_by_id(record_id)
    
    @staticmethod
    def get_by_id(record_id):
        row = fetchone('SELECT * FROM checkin_records WHERE id = %s', (record_id,))
        return CheckinRecord(**row) if row else None
    
    @staticmethod
    def get_by_user_and_date(user_id, checkin_date):
        row = fetchone(
            'SELECT * FROM checkin_records WHERE user_id = %s AND checkin_date = %s',
            (user_id, checkin_date)
        )
        return CheckinRecord(**row) if row else None
    
    @staticmethod
    def get_latest_by_user(user_id):
        row = fetchone(
            '''SELECT * FROM checkin_records 
               WHERE user_id = %s 
               ORDER BY checkin_date DESC LIMIT 1''',
            (user_id,)
        )
        return CheckinRecord(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=30, offset=0):
        rows = fetchall(
            '''SELECT * FROM checkin_records 
               WHERE user_id = %s 
               ORDER BY checkin_date DESC LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return [CheckinRecord(**row) for row in rows]
    
    @staticmethod
    def count_continuous_days(user_id, reference_date=None):
        if reference_date is None:
            reference_date = date.today()
        
        yesterday = reference_date - timedelta(days=1)
        
        latest_record = CheckinRecord.get_latest_by_user(user_id)
        if not latest_record:
            return 0
        
        latest_date = latest_record.checkin_date
        if isinstance(latest_date, str):
            latest_date = datetime.strptime(latest_date, '%Y-%m-%d').date()
        
        if latest_date == reference_date:
            return latest_record.continuous_days
        elif latest_date == yesterday:
            return latest_record.continuous_days
        else:
            return 0
    
    @staticmethod
    def check_today(user_id):
        today = date.today()
        record = CheckinRecord.get_by_user_and_date(user_id, today)
        return record is not None
    
    def get_user(self):
        if self._user is None:
            self._user = User.get_by_id(self.user_id)
        return self._user
    
    def to_dict(self, include_user=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'checkin_date': self.checkin_date,
            'points_earned': self.points_earned,
            'continuous_days': self.continuous_days,
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
