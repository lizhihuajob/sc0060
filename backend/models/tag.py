from datetime import datetime
from database import execute, fetchone, fetchall

class Tag:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.slug = kwargs.get('slug')
        self.description = kwargs.get('description')
        self.color = kwargs.get('color', '#0071e3')
        self.icon = kwargs.get('icon')
        self.sort_order = kwargs.get('sort_order', 0)
        self.is_active = kwargs.get('is_active', 1)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self._posts_count = None
    
    @staticmethod
    def create(name, slug=None, description=None, color='#0071e3', icon=None, sort_order=0):
        from datetime import datetime
        
        now = datetime.now()
        actual_slug = slug or name.lower().replace(' ', '-').replace('_', '-')
        
        tag_id = execute(
            '''INSERT INTO tags (name, slug, description, color, icon, sort_order, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
            (name, actual_slug, description, color, icon, sort_order, now, now)
        )
        return Tag.get_by_id(tag_id)
    
    @staticmethod
    def get_by_id(tag_id):
        row = fetchone('SELECT * FROM tags WHERE id = %s', (tag_id,))
        return Tag(**row) if row else None
    
    @staticmethod
    def get_by_slug(slug):
        row = fetchone('SELECT * FROM tags WHERE slug = %s', (slug,))
        return Tag(**row) if row else None
    
    @staticmethod
    def get_by_name(name):
        row = fetchone('SELECT * FROM tags WHERE name = %s', (name,))
        return Tag(**row) if row else None
    
    @staticmethod
    def get_all(include_inactive=False, limit=None, offset=0):
        conditions = ['1=1']
        params = []
        
        if not include_inactive:
            conditions.append('is_active = 1')
        
        where_clause = ' AND '.join(conditions)
        
        if limit:
            query = f'''SELECT * FROM tags WHERE {where_clause} 
                        ORDER BY sort_order ASC, created_at DESC LIMIT %s OFFSET %s'''
            params.extend([limit, offset])
        else:
            query = f'''SELECT * FROM tags WHERE {where_clause} 
                        ORDER BY sort_order ASC, created_at DESC'''
        
        rows = fetchall(query, params)
        return [Tag(**row) for row in rows]
    
    @staticmethod
    def get_for_admin(limit=20, offset=0, keyword=None, is_active=None):
        conditions = ['1=1']
        params = []
        
        if keyword:
            conditions.append('(name ILIKE %s OR slug ILIKE %s OR description ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param, keyword_param])
        
        if is_active is not None:
            conditions.append('is_active = %s')
            params.append(1 if is_active else 0)
        
        where_clause = ' AND '.join(conditions)
        
        query = f'''SELECT * FROM tags WHERE {where_clause} 
                    ORDER BY sort_order ASC, created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Tag(**row) for row in rows]
    
    @staticmethod
    def count_for_admin(keyword=None, is_active=None):
        conditions = ['1=1']
        params = []
        
        if keyword:
            conditions.append('(name ILIKE %s OR slug ILIKE %s OR description ILIKE %s)')
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param, keyword_param])
        
        if is_active is not None:
            conditions.append('is_active = %s')
            params.append(1 if is_active else 0)
        
        where_clause = ' AND '.join(conditions)
        
        query = f'''SELECT COUNT(*) as count FROM tags WHERE {where_clause}'''
        
        row = fetchone(query, params)
        return row['count'] if row else 0
    
    @staticmethod
    def get_by_post(post_id):
        query = '''
            SELECT t.* FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            WHERE pt.post_id = %s AND t.is_active = 1
            ORDER BY t.sort_order ASC
        '''
        rows = fetchall(query, (post_id,))
        return [Tag(**row) for row in rows]
    
    def update(self, name=None, slug=None, description=None, color=None, icon=None, sort_order=None, is_active=None):
        from datetime import datetime
        
        updates = {}
        if name is not None:
            updates['name'] = name
        if slug is not None:
            updates['slug'] = slug
        if description is not None:
            updates['description'] = description
        if color is not None:
            updates['color'] = color
        if icon is not None:
            updates['icon'] = icon
        if sort_order is not None:
            updates['sort_order'] = sort_order
        if is_active is not None:
            updates['is_active'] = 1 if is_active else 0
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now()
        
        set_clause = ', '.join([f'{key} = %s' for key in updates.keys()])
        params = list(updates.values()) + [self.id]
        
        query = f'UPDATE tags SET {set_clause} WHERE id = %s'
        execute(query, params)
        
        for key, value in updates.items():
            setattr(self, key, value)
        
        return True
    
    def delete(self):
        execute('DELETE FROM post_tags WHERE tag_id = %s', (self.id,))
        execute('DELETE FROM tags WHERE id = %s', (self.id,))
        return True
    
    def get_posts_count(self):
        if self._posts_count is None:
            row = fetchone(
                'SELECT COUNT(*) as count FROM post_tags WHERE tag_id = %s',
                (self.id,)
            )
            self._posts_count = row['count'] if row else 0
        return self._posts_count
    
    def to_dict(self, include_posts_count=False):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_posts_count:
            data['posts_count'] = self.get_posts_count()
        
        return data


class PostTag:
    @staticmethod
    def add_tags_to_post(post_id, tag_ids):
        if not tag_ids:
            return
        
        existing_tags = [pt['tag_id'] for pt in fetchall(
            'SELECT tag_id FROM post_tags WHERE post_id = %s',
            (post_id,)
        )]
        
        for tag_id in tag_ids:
            if tag_id not in existing_tags:
                execute(
                    'INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)',
                    (post_id, tag_id)
                )
    
    @staticmethod
    def set_post_tags(post_id, tag_ids):
        execute('DELETE FROM post_tags WHERE post_id = %s', (post_id,))
        
        if tag_ids:
            for tag_id in tag_ids:
                execute(
                    'INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)',
                    (post_id, tag_id)
                )
    
    @staticmethod
    def remove_tag_from_post(post_id, tag_id):
        execute(
            'DELETE FROM post_tags WHERE post_id = %s AND tag_id = %s',
            (post_id, tag_id)
        )
    
    @staticmethod
    def get_tag_ids_for_post(post_id):
        rows = fetchall(
            'SELECT tag_id FROM post_tags WHERE post_id = %s',
            (post_id,)
        )
        return [row['tag_id'] for row in rows]
    
    @staticmethod
    def get_posts_by_tag(tag_id, limit=20, offset=0):
        query = '''
            SELECT p.* FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            WHERE pt.tag_id = %s AND p.status = 'active'
            ORDER BY p.created_at DESC LIMIT %s OFFSET %s
        '''
        rows = fetchall(query, (tag_id, limit, offset))
        from models.post import Post
        return [Post(**row) for row in rows]
