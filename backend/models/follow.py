from database import execute, fetchone, fetchall
from datetime import datetime

class Follow:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.follower_id = kwargs.get('follower_id')
        self.following_id = kwargs.get('following_id')
        self.created_at = kwargs.get('created_at')
        self._follower = None
        self._following = None
    
    @staticmethod
    def create(follower_id, following_id):
        if follower_id == following_id:
            return None
        
        existing = Follow.get_by_users(follower_id, following_id)
        if existing:
            return existing
        
        now = datetime.now()
        follow_id = execute(
            '''INSERT INTO follows (follower_id, following_id, created_at)
               VALUES (%s, %s, %s) RETURNING id''',
            (follower_id, following_id, now)
        )
        return Follow.get_by_id(follow_id)
    
    @staticmethod
    def get_by_id(follow_id):
        row = fetchone('SELECT * FROM follows WHERE id = %s', (follow_id,))
        return Follow(**row) if row else None
    
    @staticmethod
    def get_by_users(follower_id, following_id):
        row = fetchone(
            'SELECT * FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id)
        )
        return Follow(**row) if row else None
    
    @staticmethod
    def is_following(follower_id, following_id):
        row = fetchone(
            'SELECT id FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id)
        )
        return row is not None
    
    @staticmethod
    def get_followers(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT f.*, u.* 
               FROM follows f 
               JOIN users u ON f.follower_id = u.id 
               WHERE f.following_id = %s 
               ORDER BY f.created_at DESC 
               LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return rows if rows else []
    
    @staticmethod
    def get_followings(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT f.*, u.* 
               FROM follows f 
               JOIN users u ON f.following_id = u.id 
               WHERE f.follower_id = %s 
               ORDER BY f.created_at DESC 
               LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return rows if rows else []
    
    @staticmethod
    def get_follower_ids(user_id):
        rows = fetchall(
            'SELECT follower_id FROM follows WHERE following_id = %s',
            (user_id,)
        )
        return [row['follower_id'] for row in rows] if rows else []
    
    @staticmethod
    def get_following_ids(user_id):
        rows = fetchall(
            'SELECT following_id FROM follows WHERE follower_id = %s',
            (user_id,)
        )
        return [row['following_id'] for row in rows] if rows else []
    
    @staticmethod
    def count_followers(user_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM follows WHERE following_id = %s',
            (user_id,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def count_followings(user_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM follows WHERE follower_id = %s',
            (user_id,)
        )
        return row['count'] if row else 0
    
    def delete(self):
        execute('DELETE FROM follows WHERE id = %s', (self.id,))
        return True
    
    @staticmethod
    def unfollow(follower_id, following_id):
        execute(
            'DELETE FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id)
        )
        return True
    
    def to_dict(self, include_relationship=False):
        data = {
            'id': self.id,
            'follower_id': self.follower_id,
            'following_id': self.following_id,
            'created_at': self.created_at
        }
        return data
