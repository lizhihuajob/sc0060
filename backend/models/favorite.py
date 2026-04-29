from database import execute, fetchone, fetchall
from datetime import datetime

class Favorite:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.post_id = kwargs.get('post_id')
        self.created_at = kwargs.get('created_at')
    
    @staticmethod
    def toggle(user_id, post_id):
        existing = Favorite.get_by_user_and_post(user_id, post_id)
        if existing:
            existing.delete()
            return False
        else:
            Favorite.create(user_id, post_id)
            return True
    
    @staticmethod
    def create(user_id, post_id):
        now = datetime.now()
        favorite_id = execute(
            '''INSERT INTO favorites (user_id, post_id, created_at)
               VALUES (%s, %s, %s) RETURNING id''',
            (user_id, post_id, now)
        )
        return Favorite.get_by_id(favorite_id)
    
    @staticmethod
    def get_by_id(favorite_id):
        row = fetchone('SELECT * FROM favorites WHERE id = %s', (favorite_id,))
        return Favorite(**row) if row else None
    
    @staticmethod
    def get_by_user_and_post(user_id, post_id):
        row = fetchone(
            'SELECT * FROM favorites WHERE user_id = %s AND post_id = %s',
            (user_id, post_id)
        )
        return Favorite(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT f.*, p.* 
               FROM favorites f 
               JOIN posts p ON f.post_id = p.id 
               WHERE f.user_id = %s 
               ORDER BY f.created_at DESC 
               LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return rows if rows else []
    
    @staticmethod
    def count_by_user(user_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM favorites WHERE user_id = %s',
            (user_id,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def is_favorited(user_id, post_id):
        row = fetchone(
            'SELECT id FROM favorites WHERE user_id = %s AND post_id = %s',
            (user_id, post_id)
        )
        return row is not None
    
    @staticmethod
    def get_favorited_post_ids(user_id):
        rows = fetchall(
            'SELECT post_id FROM favorites WHERE user_id = %s',
            (user_id,)
        )
        return [row['post_id'] for row in rows] if rows else []
    
    def delete(self):
        execute('DELETE FROM favorites WHERE id = %s', (self.id,))
        return True
    
    @staticmethod
    def delete_by_user_and_post(user_id, post_id):
        execute(
            'DELETE FROM favorites WHERE user_id = %s AND post_id = %s',
            (user_id, post_id)
        )
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at
        }
