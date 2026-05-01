from database import execute, fetchone, fetchall
from models.user import User
from models.post import Post

class EditLog:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.post_id = kwargs.get('post_id')
        self.user_id = kwargs.get('user_id')
        self.title_before = kwargs.get('title_before')
        self.content_before = kwargs.get('content_before')
        self.view_permission_before = kwargs.get('view_permission_before')
        self.is_task_before = kwargs.get('is_task_before')
        self.title_after = kwargs.get('title_after')
        self.content_after = kwargs.get('content_after')
        self.view_permission_after = kwargs.get('view_permission_after')
        self.is_task_after = kwargs.get('is_task_after')
        self.edit_reason = kwargs.get('edit_reason')
        self.created_at = kwargs.get('created_at')
        self._user = None
        self._post = None
    
    @staticmethod
    def create(post_id, user_id, old_data, new_data, edit_reason=None):
        log_id = execute(
            '''INSERT INTO edit_logs 
               (post_id, user_id, 
                title_before, content_before, view_permission_before, is_task_before,
                title_after, content_after, view_permission_after, is_task_after,
                edit_reason)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING id''',
            (post_id, user_id,
             old_data.get('title'), old_data.get('content'), old_data.get('view_permission'), old_data.get('is_task'),
             new_data.get('title'), new_data.get('content'), new_data.get('view_permission'), new_data.get('is_task'),
             edit_reason)
        )
        return EditLog.get_by_id(log_id)
    
    @staticmethod
    def get_by_id(log_id):
        row = fetchone('SELECT * FROM edit_logs WHERE id = %s', (log_id,))
        return EditLog(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM edit_logs WHERE user_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return [EditLog(**row) for row in rows]
    
    @staticmethod
    def get_by_post(post_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM edit_logs WHERE post_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (post_id, limit, offset)
        )
        return [EditLog(**row) for row in rows]
    
    @staticmethod
    def count_by_user(user_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM edit_logs WHERE user_id = %s',
            (user_id,)
        )
        return row['count'] if row else 0
    
    def get_user(self):
        if self._user is None:
            self._user = User.get_by_id(self.user_id)
        return self._user
    
    def get_post(self):
        if self._post is None:
            self._post = Post.get_by_id(self.post_id)
        return self._post
    
    def has_title_changed(self):
        return self.title_before != self.title_after
    
    def has_content_changed(self):
        return self.content_before != self.content_after
    
    def has_view_permission_changed(self):
        return self.view_permission_before != self.view_permission_after
    
    def has_is_task_changed(self):
        return self.is_task_before != self.is_task_after
    
    def get_changes_summary(self):
        changes = []
        if self.has_title_changed():
            changes.append('修改了标题')
        if self.has_content_changed():
            changes.append('修改了内容')
        if self.has_view_permission_changed():
            changes.append('修改了可见范围')
        if self.has_is_task_changed():
            changes.append('修改了信息类型')
        return '，'.join(changes) if changes else '无变化'
    
    def to_dict(self, include_user=False, include_post=False):
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'title_before': self.title_before,
            'content_before': self.content_before,
            'view_permission_before': self.view_permission_before,
            'is_task_before': self.is_task_before,
            'title_after': self.title_after,
            'content_after': self.content_after,
            'view_permission_after': self.view_permission_after,
            'is_task_after': self.is_task_after,
            'edit_reason': self.edit_reason,
            'changes_summary': self.get_changes_summary(),
            'created_at': self.created_at
        }
        
        if include_user:
            user = self.get_user()
            if user:
                data['user'] = {
                    'id': user.id,
                    'username': user.username
                }
        
        if include_post:
            post = self.get_post()
            if post:
                data['post'] = {
                    'id': post.id,
                    'title': post.title
                }
        
        return data
