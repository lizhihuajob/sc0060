import json
from datetime import datetime, timedelta
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
        self.views_count = kwargs.get('views_count', 0)
        self.category = kwargs.get('category', 'other')
        self.is_pinned = kwargs.get('is_pinned', 0)
        self.pinned_until = kwargs.get('pinned_until')
        self.created_at = kwargs.get('created_at')
        self._author = None
    
    @staticmethod
    def create(user_id, title, content, view_permission='all', images=None, is_task=0, category='other'):
        images_json = json.dumps(images) if images else None
        post_id = execute(
            '''INSERT INTO posts (user_id, title, content, view_permission, images, is_task, category)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
            (user_id, title, content, view_permission, images_json, is_task, category)
        )
        return Post.get_by_id(post_id)
    
    @staticmethod
    def get_by_id(post_id):
        row = fetchone('SELECT * FROM posts WHERE id = %s', (post_id,))
        return Post(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM posts WHERE user_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return [Post(**row) for row in rows]
    
    @staticmethod
    def get_active_pinned_posts(current_user=None, limit=3):
        now = datetime.now()
        base_conditions = ['is_pinned = %s', '(pinned_until IS NULL OR pinned_until > %s)']
        params = [1, now]
        
        if current_user is None:
            base_conditions.append('view_permission = %s')
            params.append('all')
        else:
            user_level = current_user.level
            level_order = list(Config.USER_LEVELS.keys())
            user_level_index = level_order.index(user_level)
            
            visibility_conditions = ['view_permission = %s']
            params.append('all')
            
            visibility_conditions.append('view_permission = %s')
            params.append('registered')
            
            silver_index = level_order.index('silver')
            if user_level_index >= silver_index:
                visibility_conditions.append('view_permission = %s')
                params.append('silver_above')
            
            gold_index = level_order.index('gold')
            if user_level_index >= gold_index:
                visibility_conditions.append('view_permission = %s')
                params.append('gold_above')
            
            visibility_str = ' OR '.join(visibility_conditions)
            base_conditions.append(f'({visibility_str})')
        
        where_clause = ' AND '.join(base_conditions)
        query = f'''SELECT * FROM posts WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT %s'''
        params.append(limit)
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
    @staticmethod
    def get_visible_posts(current_user=None, category=None, limit=20, offset=0):
        if current_user is None:
            return Post._get_public_posts(category, limit, offset)
        
        user_level = current_user.level
        level_order = list(Config.USER_LEVELS.keys())
        user_level_index = level_order.index(user_level)
        
        conditions = ['view_permission = %s']
        params = ['all']
        
        conditions.append('view_permission = %s')
        params.append('registered')
        
        silver_index = level_order.index('silver')
        if user_level_index >= silver_index:
            conditions.append('view_permission = %s')
            params.append('silver_above')
        
        gold_index = level_order.index('gold')
        if user_level_index >= gold_index:
            conditions.append('view_permission = %s')
            params.append('gold_above')
        
        if category and category != 'all':
            conditions.append('category = %s')
            params.append(category)
        
        conditions.append('is_pinned = %s')
        params.append(0)
        
        where_clause = ' OR '.join(conditions[:-2])
        where_clause = f'({where_clause}) AND {conditions[-2]} AND {conditions[-1]}'
        query = f'''SELECT * FROM posts WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
    @staticmethod
    def _get_public_posts(category=None, limit=20, offset=0):
        conditions = ['view_permission = %s']
        params = ['all']
        
        if category and category != 'all':
            conditions.append('category = %s')
            params.append(category)
        
        conditions.append('is_pinned = %s')
        params.append(0)
        
        where_clause = ' AND '.join(conditions)
        query = f'''SELECT * FROM posts WHERE {where_clause} 
                   ORDER BY created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
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
    
    def is_owned_by(self, user):
        if user is None:
            return False
        return self.user_id == user.id
    
    def increment_views(self):
        execute(
            'UPDATE posts SET views_count = views_count + 1 WHERE id = %s',
            (self.id,)
        )
        self.views_count += 1
        return True
    
    def pin(self, duration_days=None):
        if duration_days is None:
            duration_days = Config.PINNED_CONFIG['duration_days']
        pinned_until = datetime.now() + timedelta(days=duration_days)
        execute(
            'UPDATE posts SET is_pinned = %s, pinned_until = %s WHERE id = %s',
            (1, pinned_until, self.id)
        )
        self.is_pinned = 1
        self.pinned_until = pinned_until
        return True
    
    def unpin(self):
        execute(
            'UPDATE posts SET is_pinned = %s, pinned_until = %s WHERE id = %s',
            (0, None, self.id)
        )
        self.is_pinned = 0
        self.pinned_until = None
        return True
    
    def delete(self):
        execute('DELETE FROM posts WHERE id = %s', (self.id,))
        return True
    
    @staticmethod
    def search_posts(current_user=None, keyword=None, post_type=None, sort_by='latest', category=None, limit=20, offset=0):
        base_conditions = []
        params = []
        
        if current_user is None:
            base_conditions.append('view_permission = %s')
            params.append('all')
        else:
            user_level = current_user.level
            level_order = list(Config.USER_LEVELS.keys())
            user_level_index = level_order.index(user_level)
            
            visibility_conditions = ['view_permission = %s']
            params.append('all')
            
            visibility_conditions.append('view_permission = %s')
            params.append('registered')
            
            silver_index = level_order.index('silver')
            if user_level_index >= silver_index:
                visibility_conditions.append('view_permission = %s')
                params.append('silver_above')
            
            gold_index = level_order.index('gold')
            if user_level_index >= gold_index:
                visibility_conditions.append('view_permission = %s')
                params.append('gold_above')
            
            visibility_str = ' OR '.join(visibility_conditions)
            base_conditions.append(f'({visibility_str})')
        
        if keyword:
            base_conditions.append('(title ILIKE %s OR content ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param])
        
        if post_type is not None:
            if post_type == 'notice':
                base_conditions.append('is_task = %s')
                params.append(0)
            elif post_type == 'task':
                base_conditions.append('is_task = %s')
                params.append(1)
        
        if category and category != 'all':
            base_conditions.append('category = %s')
            params.append(category)
        
        base_conditions.append('is_pinned = %s')
        params.append(0)
        
        where_clause = ' AND '.join(base_conditions) if base_conditions else '1=1'
        
        order_clause = 'created_at DESC'
        if sort_by == 'hot':
            order_clause = 'views_count DESC, created_at DESC'
        
        query = f'''SELECT * FROM posts WHERE {where_clause} 
                    ORDER BY {order_clause} LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
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
    
    def get_category_name(self):
        return Config.CATEGORIES.get(self.category, '其他')
    
    def is_pinned_active(self):
        if not self.is_pinned:
            return False
        if self.pinned_until is None:
            return True
        return datetime.now() < self.pinned_until
    
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
            'views_count': self.views_count,
            'category': self.category,
            'category_name': self.get_category_name(),
            'is_pinned': self.is_pinned,
            'is_pinned_active': self.is_pinned_active(),
            'pinned_until': self.pinned_until.isoformat() if self.pinned_until else None,
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
