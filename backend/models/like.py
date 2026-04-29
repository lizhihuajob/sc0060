from database import execute, fetchone, fetchall
from datetime import datetime

class Like:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.post_id = kwargs.get('post_id')
        self.created_at = kwargs.get('created_at')
    
    @staticmethod
    def toggle(user_id, post_id):
        existing = Like.get_by_user_and_post(user_id, post_id)
        if existing:
            existing.delete()
            return False, Like.count_by_post(post_id)
        else:
            Like.create(user_id, post_id)
            return True, Like.count_by_post(post_id)
    
    @staticmethod
    def create(user_id, post_id):
        now = datetime.now()
        like_id = execute(
            '''INSERT INTO likes (user_id, post_id, created_at)
               VALUES (%s, %s, %s) RETURNING id''',
            (user_id, post_id, now)
        )
        return Like.get_by_id(like_id)
    
    @staticmethod
    def get_by_id(like_id):
        row = fetchone('SELECT * FROM likes WHERE id = %s', (like_id,))
        return Like(**row) if row else None
    
    @staticmethod
    def get_by_user_and_post(user_id, post_id):
        row = fetchone(
            'SELECT * FROM likes WHERE user_id = %s AND post_id = %s',
            (user_id, post_id)
        )
        return Like(**row) if row else None
    
    @staticmethod
    def count_by_post(post_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM likes WHERE post_id = %s',
            (post_id,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def is_liked(user_id, post_id):
        row = fetchone(
            'SELECT id FROM likes WHERE user_id = %s AND post_id = %s',
            (user_id, post_id)
        )
        return row is not None
    
    @staticmethod
    def get_liked_post_ids(user_id):
        rows = fetchall(
            'SELECT post_id FROM likes WHERE user_id = %s',
            (user_id,)
        )
        return [row['post_id'] for row in rows] if rows else []
    
    @staticmethod
    def get_post_likes_count_batch(post_ids):
        if not post_ids:
            return {}
        placeholders = ', '.join(['%s'] * len(post_ids))
        rows = fetchall(
            f'''SELECT post_id, COUNT(*) as count FROM likes 
                WHERE post_id IN ({placeholders}) 
                GROUP BY post_id''',
            post_ids
        )
        result = {}
        for row in rows:
            result[row['post_id']] = row['count']
        return result
    
    def delete(self):
        execute('DELETE FROM likes WHERE id = %s', (self.id,))
        return True
    
    @staticmethod
    def delete_by_user_and_post(user_id, post_id):
        execute(
            'DELETE FROM likes WHERE user_id = %s AND post_id = %s',
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
