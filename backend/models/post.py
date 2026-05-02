import json
from database import execute, fetchone, fetchall
from config import Config
from models.user import User

class Post:
    STATUS_ACTIVE = 'active'
    STATUS_HIDDEN = 'hidden'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.title = kwargs.get('title')
        self.content = kwargs.get('content')
        self.view_permission = kwargs.get('view_permission', 'all')
        self.images = kwargs.get('images')
        self.is_task = kwargs.get('is_task', 0)
        self.views_count = kwargs.get('views_count', 0)
        self.is_pinned = kwargs.get('is_pinned', 0)
        self.pinned_at = kwargs.get('pinned_at')
        self.pin_expires_at = kwargs.get('pin_expires_at')
        self.status = kwargs.get('status', self.STATUS_ACTIVE)
        self.hidden_by = kwargs.get('hidden_by')
        self.hidden_at = kwargs.get('hidden_at')
        self.hidden_reason = kwargs.get('hidden_reason')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self._author = None
        self._hidden_by_admin = None
    
    @staticmethod
    def create(user_id, title, content, view_permission='all', images=None, is_task=0):
        images_json = json.dumps(images) if images else None
        post_id = execute(
            '''INSERT INTO posts (user_id, title, content, view_permission, images, is_task)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id''',
            (user_id, title, content, view_permission, images_json, is_task)
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
    def get_visible_posts(current_user=None, limit=20, offset=0):
        if current_user is None:
            return Post._get_public_posts(limit, offset)
        
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
        
        conditions.append('(is_pinned = 0 OR is_pinned IS NULL)')
        conditions.append('status = %s')
        params.append(Post.STATUS_ACTIVE)
        
        where_clause = ' OR '.join(conditions[:-2]) + ' AND ' + ' AND '.join(conditions[-2:])
        query = f'''SELECT * FROM posts WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
    @staticmethod
    def _get_public_posts(limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM posts 
               WHERE view_permission = %s AND (is_pinned = 0 OR is_pinned IS NULL) AND status = %s
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            ('all', Post.STATUS_ACTIVE, limit, offset)
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
    
    def update(self, title=None, content=None, view_permission=None, images=None, is_task=None):
        from datetime import datetime
        
        updates = {}
        if title is not None:
            updates['title'] = title
        if content is not None:
            updates['content'] = content
        if view_permission is not None:
            updates['view_permission'] = view_permission
        if images is not None:
            updates['images'] = json.dumps(images) if images else None
        if is_task is not None:
            updates['is_task'] = is_task
        
        if not updates:
            return False
        
        now = datetime.now()
        updates['updated_at'] = now
        
        set_clause = ', '.join([f'{key} = %s' for key in updates.keys()])
        params = list(updates.values()) + [self.id]
        
        query = f'UPDATE posts SET {set_clause} WHERE id = %s'
        execute(query, params)
        
        for key, value in updates.items():
            setattr(self, key, value)
        
        return True
    
    def get_old_data(self):
        return {
            'title': self.title,
            'content': self.content,
            'view_permission': self.view_permission,
            'is_task': self.is_task
        }
    
    def delete(self):
        execute('DELETE FROM posts WHERE id = %s', (self.id,))
        return True
    
    def pin(self, duration_days=7):
        from datetime import datetime, timedelta
        now = datetime.now()
        expires_at = now + timedelta(days=duration_days)
        execute(
            '''UPDATE posts SET is_pinned = %s, pinned_at = %s, pin_expires_at = %s WHERE id = %s''',
            (1, now, expires_at, self.id)
        )
        self.is_pinned = 1
        self.pinned_at = now
        self.pin_expires_at = expires_at
        return True
    
    def unpin(self):
        execute(
            '''UPDATE posts SET is_pinned = %s, pinned_at = %s, pin_expires_at = %s WHERE id = %s''',
            (0, None, None, self.id)
        )
        self.is_pinned = 0
        self.pinned_at = None
        self.pin_expires_at = None
        return True
    
    def hide(self, admin_id, reason=None):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE posts SET status = %s, hidden_by = %s, hidden_at = %s, hidden_reason = %s WHERE id = %s''',
            (self.STATUS_HIDDEN, admin_id, now, reason, self.id)
        )
        self.status = self.STATUS_HIDDEN
        self.hidden_by = admin_id
        self.hidden_at = now
        self.hidden_reason = reason
        return True
    
    def unhide(self):
        execute(
            '''UPDATE posts SET status = %s, hidden_by = %s, hidden_at = %s, hidden_reason = %s WHERE id = %s''',
            (self.STATUS_ACTIVE, None, None, None, self.id)
        )
        self.status = self.STATUS_ACTIVE
        self.hidden_by = None
        self.hidden_at = None
        self.hidden_reason = None
        return True
    
    def is_hidden(self):
        return self.status == self.STATUS_HIDDEN
    
    def get_hidden_by_admin(self):
        if self._hidden_by_admin is None and self.hidden_by:
            from models.admin import Admin
            self._hidden_by_admin = Admin.get_by_id(self.hidden_by)
        return self._hidden_by_admin
    
    @staticmethod
    def get_active_pinned_posts(current_user=None, limit=3):
        from datetime import datetime
        now = datetime.now()
        
        base_conditions = ['is_pinned = 1', '(pin_expires_at IS NULL OR pin_expires_at > %s)', 'status = %s']
        params = [now, Post.STATUS_ACTIVE]
        
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
                    ORDER BY pinned_at DESC LIMIT %s'''
        params.append(limit)
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
    @staticmethod
    def get_pinned_count():
        from datetime import datetime
        now = datetime.now()
        row = fetchone(
            '''SELECT COUNT(*) as count FROM posts 
               WHERE is_pinned = 1 AND (pin_expires_at IS NULL OR pin_expires_at > %s)''',
            (now,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def search_posts(current_user=None, keyword=None, post_type=None, sort_by='latest', tag_id=None, limit=20, offset=0):
        base_conditions = ['(is_pinned = 0 OR is_pinned IS NULL)', 'status = %s']
        params = [Post.STATUS_ACTIVE]
        
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
        
        if tag_id:
            base_conditions.append('id IN (SELECT post_id FROM post_tags WHERE tag_id = %s)')
            params.append(tag_id)
        
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
    
    @staticmethod
    def get_all_for_admin(limit=20, offset=0, status=None, keyword=None, tag_id=None):
        base_conditions = ['1=1']
        params = []
        
        if status:
            base_conditions.append('status = %s')
            params.append(status)
        
        if keyword:
            base_conditions.append('(title ILIKE %s OR content ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param])
        
        if tag_id:
            base_conditions.append('p.id IN (SELECT post_id FROM post_tags WHERE tag_id = %s)')
            params.append(tag_id)
        
        where_clause = ' AND '.join(base_conditions)
        
        query = f'''SELECT p.* FROM posts p WHERE {where_clause} 
                    ORDER BY p.created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Post(**row) for row in rows]
    
    @staticmethod
    def count_for_admin(status=None, keyword=None, tag_id=None):
        base_conditions = ['1=1']
        params = []
        
        if status:
            base_conditions.append('status = %s')
            params.append(status)
        
        if keyword:
            base_conditions.append('(title ILIKE %s OR content ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param])
        
        if tag_id:
            base_conditions.append('id IN (SELECT post_id FROM post_tags WHERE tag_id = %s)')
            params.append(tag_id)
        
        where_clause = ' AND '.join(base_conditions)
        
        query = f'''SELECT COUNT(*) as count FROM posts WHERE {where_clause}'''
        
        row = fetchone(query, params)
        return row['count'] if row else 0
    
    @staticmethod
    def get_total_views():
        row = fetchone(
            'SELECT SUM(views_count) as total FROM posts',
            ()
        )
        return row['total'] if row and row['total'] else 0
    
    @staticmethod
    def get_popular_posts(limit=10, offset=0):
        query = '''
            SELECT * FROM posts 
            WHERE status = %s 
            ORDER BY views_count DESC, created_at DESC 
            LIMIT %s OFFSET %s
        '''
        rows = fetchall(query, (Post.STATUS_ACTIVE, limit, offset))
        return [Post(**row) for row in rows]
    
    @staticmethod
    def get_daily_views_stats(start_date, end_date):
        query = '''
            SELECT 
                DATE(created_at) as date,
                SUM(views_count) as total_views
            FROM posts
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY date
        '''
        rows = fetchall(query, (start_date, end_date))
        return rows if rows else []
    
    @staticmethod
    def get_daily_posts_stats(start_date, end_date):
        query = '''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM posts
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY date
        '''
        rows = fetchall(query, (start_date, end_date))
        return rows if rows else []
    
    def get_tags(self):
        from models.tag import Tag
        return Tag.get_by_post(self.id)
    
    def to_dict(self, include_author=False, include_admin_info=False, include_tags=False):
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
            'is_pinned': self.is_pinned,
            'pinned_at': self.pinned_at,
            'pin_expires_at': self.pin_expires_at,
            'status': self.status,
            'is_hidden': self.is_hidden(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_admin_info:
            data['hidden_by'] = self.hidden_by
            data['hidden_at'] = self.hidden_at
            data['hidden_reason'] = self.hidden_reason
            
            hidden_admin = self.get_hidden_by_admin()
            if hidden_admin:
                data['hidden_by_admin'] = {
                    'id': hidden_admin.id,
                    'username': hidden_admin.username
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
        
        if include_tags:
            tags = self.get_tags()
            data['tags'] = [tag.to_dict() for tag in tags]
        
        return data
