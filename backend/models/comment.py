from database import execute, fetchone, fetchall
from models.user import User

class Comment:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.post_id = kwargs.get('post_id')
        self.user_id = kwargs.get('user_id')
        self.parent_id = kwargs.get('parent_id')
        self.reply_to_user_id = kwargs.get('reply_to_user_id')
        self.content = kwargs.get('content')
        self.created_at = kwargs.get('created_at')
        self._author = None
        self._reply_to_user = None
        self._parent = None
        self._replies = []
    
    @staticmethod
    def create(post_id, user_id, content, parent_id=None, reply_to_user_id=None):
        comment_id = execute(
            '''INSERT INTO comments (post_id, user_id, content, parent_id, reply_to_user_id)
               VALUES (%s, %s, %s, %s, %s) RETURNING id''',
            (post_id, user_id, content, parent_id, reply_to_user_id)
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
    
    @staticmethod
    def count_total():
        row = fetchone(
            'SELECT COUNT(*) as cnt FROM comments',
            ()
        )
        return row['cnt'] if row else 0
    
    @staticmethod
    def get_daily_stats(start_date, end_date):
        query = '''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM comments
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY date
        '''
        rows = fetchall(query, (start_date, end_date))
        return rows if rows else []
    
    def get_author(self):
        if self._author is None:
            self._author = User.get_by_id(self.user_id)
        return self._author
    
    def get_reply_to_user(self):
        if self._reply_to_user is None and self.reply_to_user_id:
            self._reply_to_user = User.get_by_id(self.reply_to_user_id)
        return self._reply_to_user
    
    def get_parent(self):
        if self._parent is None and self.parent_id:
            self._parent = Comment.get_by_id(self.parent_id)
        return self._parent
    
    def get_replies(self):
        if not self._replies:
            rows = fetchall(
                '''SELECT * FROM comments WHERE parent_id = %s 
                   ORDER BY created_at ASC''',
                (self.id,)
            )
            self._replies = [Comment(**row) for row in rows]
        return self._replies
    
    @staticmethod
    def get_by_post_with_replies(post_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM comments WHERE post_id = %s AND parent_id IS NULL
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (post_id, limit, offset)
        )
        comments = [Comment(**row) for row in rows]
        return comments
    
    def is_owned_by(self, user):
        if user is None:
            return False
        return self.user_id == user.id
    
    def delete(self):
        execute('DELETE FROM comments WHERE id = %s', (self.id,))
        return True
    
    def to_dict(self, include_author=False, include_replies=False):
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'reply_to_user_id': self.reply_to_user_id,
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
        
        if self.reply_to_user_id:
            reply_to_user = self.get_reply_to_user()
            if reply_to_user:
                data['reply_to_user'] = {
                    'id': reply_to_user.id,
                    'username': reply_to_user.username
                }
        
        if include_replies:
            replies = self.get_replies()
            data['replies'] = [r.to_dict(include_author=True, include_replies=True) for r in replies]
        
        return data
