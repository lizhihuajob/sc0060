import json
from database import execute, fetchone, fetchall
from config import Config
from models.user import User

class Post:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.title = kwargs.get('title')
        self.content = kwargs.get('content')
        self.view_permission = kwargs.get('view_permission', 'all')
        self.images = kwargs.get('images')
        self.is_task = kwargs.get('is_task', 0)
        self.created_at = kwargs.get('created_at')
        self._author = None
    
    @staticmethod
    def create(user_id, title, content, view_permission='all', images=None, is_task=0):
        images_json = json.dumps(images) if images else None
        post_id = execute(
            '''INSERT INTO posts (user_id, title, content, view_permission, images, is_task)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, title, content, view_permission, images_json, is_task)
        )
        return Post.get_by_id(post_id)
    
    @staticmethod
    def get_by_id(post_id):
        row = fetchone('SELECT * FROM posts WHERE id = ?', (post_id,))
        return Post(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM posts WHERE user_id = ? 
               ORDER BY created_at DESC LIMIT ? OFFSET ?''',
            (user_id, limit, offset)
        )
        return [Post(**row) for row in rows]
    
    @staticmethod
    def get_visible_posts(current_user=None, limit=20, offset=0):
        if current_user is None:
            return Post._get_public_posts(limit, offset)
        
        user_level = current_user.level
        level_order = list(Config.USER_LEVELS.keys())
        user_level_index = level_order.index(user_level)
        
        conditions = ['view_permission = ?']
        params = ['all']
        
        conditions.append('view_permission = ?')
        params.append('registered')
        
        silver_index = level_order.index('silver')
        if user_level_index >= silver_index:
            conditions.append('view_permission = ?')
            params.append('silver_above')
        
        gold_index = level_order.index('gold')
        if user_level_index >= gold_index:
            conditions.append('view_permission = ?')
            params.append('gold_above')
        
        where_clause = ' OR '.join(conditions)
        query = f'''SELECT * FROM posts WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT ? OFFSET ?'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
    @staticmethod
    def _get_public_posts(limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM posts WHERE view_permission = ? 
               ORDER BY created_at DESC LIMIT ? OFFSET ?''',
            ('all', limit, offset)
        )
        return [Post(**row) for row in rows]
    
    def is_visible_to(self, user):
        if self.view_permission == 'all':
            return True
        
        if user is None:
            return False
        
        level_order = list(Config.USER_LEVELS.keys())
        user_level_index = level_order.index(user.level)
        
        if self.view_permission == 'registered':
            return True
        
        if self.view_permission == 'silver_above':
            silver_index = level_order.index('silver')
            return user_level_index >= silver_index
        
        if self.view_permission == 'gold_above':
            gold_index = level_order.index('gold')
            return user_level_index >= gold_index
        
        return False
    
    def get_author(self):
        if self._author is None:
            self._author = User.get_by_id(self.user_id)
        return self._author
    
    def get_images_list(self):
        if self.images:
            try:
                return json.loads(self.images)
            except:
                return []
        return []
    
    def get_view_permission_name(self):
        return Config.VIEW_PERMISSIONS.get(self.view_permission, '所有用户')
    
    def to_dict(self, include_author=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'view_permission': self.view_permission,
            'view_permission_name': self.get_view_permission_name(),
            'images': self.get_images_list(),
            'is_task': self.is_task,
            'created_at': self.created_at
        }
        
        if include_author:
            author = self.get_author()
            if author:
                data['author'] = {
                    'id': author.id,
                    'username': author.username,
                    'level': author.level,
                    'level_name': author.get_level_info()['name']
                }
        
        return data
