from database import execute, fetchone, fetchall
from models.user import User

class Comment:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.post_id = kwargs.get('post_id')
        self.user_id = kwargs.get('user_id')
        self.content = kwargs.get('content')
        self.created_at = kwargs.get('created_at')
        self._author = None
    
    @staticmethod
    def create(post_id, user_id, content):
        comment_id = execute(
            '''INSERT INTO comments (post_id, user_id, content)
               VALUES (%s, %s, %s) RETURNING id''',
            (post_id, user_id, content)
        )
        return Comment.get_by_id(comment_id)
    
    @staticmethod
    def get_by_id(comment_id):
        row = fetchone('SELECT * FROM comments WHERE id = %s', (comment_id,))
        return Comment(**row) if row else None
    
    @staticmethod
    def get_by_post(post_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM comments WHERE post_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (post_id, limit, offset)
        )
        return [Comment(**row) for row in rows]
    
    @staticmethod
    def count_by_post(post_id):
        row = fetchone(
            'SELECT COUNT(*) as cnt FROM comments WHERE post_id = %s',
            (post_id,)
        )
        return row['cnt'] if row else 0
    
    def get_author(self):
        if self._author is None:
            self._author = User.get_by_id(self.user_id)
        return self._author
    
    def is_owned_by(self, user):
        if user is None:
            return False
        return self.user_id == user.id
    
    def delete(self):
        execute('DELETE FROM comments WHERE id = %s', (self.id,))
        return True
    
    def to_dict(self, include_author=False):
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at
        }
        
        if include_author:
            author = self.get_author()
            if author:
                data['author'] = {
                    'id': author.id,
                    'username': author.username,
                    'avatar': author.avatar,
                    'level': author.level,
                    'level_name': author.get_level_info()['name']
                }
        
        return data
