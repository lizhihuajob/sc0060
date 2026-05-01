from database import execute, fetchone, fetchall

class Announcement:
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.admin_id = kwargs.get('admin_id')
        self.title = kwargs.get('title')
        self.content = kwargs.get('content')
        self.is_pinned = kwargs.get('is_pinned', 0)
        self.pinned_at = kwargs.get('pinned_at')
        self.status = kwargs.get('status', self.STATUS_ACTIVE)
        self.publish_at = kwargs.get('publish_at')
        self.expires_at = kwargs.get('expires_at')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self._admin = None
    
    @staticmethod
    def create(admin_id, title, content, is_pinned=0, publish_at=None, expires_at=None):
        from datetime import datetime
        
        now = datetime.now()
        
        values = [admin_id, title, content, is_pinned]
        
        if is_pinned:
            values.append(now)
        else:
            values.append(None)
        
        values.extend([publish_at, expires_at])
        
        announcement_id = execute(
            '''INSERT INTO announcements (admin_id, title, content, is_pinned, pinned_at, publish_at, expires_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
            tuple(values)
        )
        return Announcement.get_by_id(announcement_id)
    
    @staticmethod
    def get_by_id(announcement_id):
        row = fetchone('SELECT * FROM announcements WHERE id = %s', (announcement_id,))
        return Announcement(**row) if row else None
    
    @staticmethod
    def get_active(current_user=None, limit=10, offset=0):
        from datetime import datetime
        now = datetime.now()
        
        base_conditions = ['status = %s', '(publish_at IS NULL OR publish_at <= %s', '(expires_at IS NULL OR expires_at > %s)']
        params = [Announcement.STATUS_ACTIVE, now, now]
        
        order_clause = 'is_pinned DESC, pinned_at DESC, created_at DESC'
        
        query = f'''SELECT * FROM announcements WHERE {' AND '.join(base_conditions)} 
                    ORDER BY {order_clause} LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Announcement(**row) for row in rows]
    
    @staticmethod
    def get_pinned(current_user=None, limit=3):
        from datetime import datetime
        now = datetime.now()
        
        rows = fetchall(
            '''SELECT * FROM announcements 
               WHERE status = %s AND is_pinned = 1 
               AND (publish_at IS NULL OR publish_at <= %s) 
               AND (expires_at IS NULL OR expires_at > %s)
               ORDER BY pinned_at DESC LIMIT %s''',
            (Announcement.STATUS_ACTIVE, now, now, limit)
        )
        return [Announcement(**row) for row in rows]
    
    @staticmethod
    def get_for_admin(limit=20, offset=0, status=None):
        base_conditions = ['1=1']
        params = []
        
        if status:
            base_conditions.append('status = %s')
            params.append(status)
        
        where_clause = ' AND '.join(base_conditions)
        query = f'''SELECT * FROM announcements WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Announcement(**row) for row in rows]
    
    @staticmethod
    def count_for_admin(status=None):
        base_conditions = ['1=1']
        params = []
        
        if status:
            base_conditions.append('status = %s')
            params.append(status)
        
        where_clause = ' AND '.join(base_conditions)
        query = f'''SELECT COUNT(*) as count FROM announcements WHERE {where_clause}'''
        
        row = fetchone(query, params)
        return row['count'] if row else 0
    
    def is_active(self):
        return self.status == self.STATUS_ACTIVE
    
    def update(self, title=None, content=None, is_pinned=None, status=None, publish_at=None, expires_at=None):
        from datetime import datetime
        
        updates = {}
        if title is not None:
            updates['title'] = title
        if content is not None:
            updates['content'] = content
        if status is not None:
            updates['status'] = status
        if publish_at is not None:
            updates['publish_at'] = publish_at
        if expires_at is not None:
            updates['expires_at'] = expires_at
        
        now = datetime.now()
        
        if is_pinned is not None:
            updates['is_pinned'] = is_pinned
            if is_pinned and not self.is_pinned:
                updates['pinned_at'] = now
            elif not is_pinned and self.is_pinned:
                updates['pinned_at'] = None
        
        if not updates:
            return False
        
        updates['updated_at'] = now
        
        set_clause = ', '.join([f'{key} = %s' for key in updates.keys()])
        params = list(updates.values()) + [self.id]
        
        query = f'UPDATE announcements SET {set_clause} WHERE id = %s'
        execute(query, params)
        
        for key, value in updates.items():
            setattr(self, key, value)
        
        return True
    
    def pin(self):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE announcements SET is_pinned = %s, pinned_at = %s, updated_at = %s WHERE id = %s''',
            (1, now, now, self.id)
        )
        self.is_pinned = 1
        self.pinned_at = now
        self.updated_at = now
        return True
    
    def unpin(self):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE announcements SET is_pinned = %s, pinned_at = %s, updated_at = %s WHERE id = %s''',
            (0, None, now, self.id)
        )
        self.is_pinned = 0
        self.pinned_at = None
        self.updated_at = now
        return True
    
    def deactivate(self):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE announcements SET status = %s, updated_at = %s WHERE id = %s''',
            (self.STATUS_INACTIVE, now, self.id)
        )
        self.status = self.STATUS_INACTIVE
        self.updated_at = now
        return True
    
    def activate(self):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE announcements SET status = %s, updated_at = %s WHERE id = %s''',
            (self.STATUS_ACTIVE, now, self.id)
        )
        self.status = self.STATUS_ACTIVE
        self.updated_at = now
        return True
    
    def delete(self):
        execute('DELETE FROM announcements WHERE id = %s', (self.id,))
        return True
    
    def get_admin(self):
        if self._admin is None and self.admin_id:
            from models.admin import Admin
            self._admin = Admin.get_by_id(self.admin_id)
        return self._admin
    
    def get_status_name(self):
        status_names = {
            self.STATUS_ACTIVE: '已发布',
            self.STATUS_INACTIVE: '已下架'
        }
        return status_names.get(self.status, '未知状态')
    
    def to_dict(self, include_admin=False):
        data = {
            'id': self.id,
            'admin_id': self.admin_id,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'pinned_at': self.pinned_at,
            'status': self.status,
            'status_name': self.get_status_name(),
            'publish_at': self.publish_at,
            'expires_at': self.expires_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_admin:
            admin = self.get_admin()
            if admin:
                data['admin'] = {
                    'id': admin.id,
                    'username': admin.username
                }
        
        return data
