from database import execute, fetchone, fetchall

class Report:
    TYPE_POST = 'post'
    TYPE_COMMENT = 'comment'
    TYPE_USER = 'user'
    
    STATUS_PENDING = 'pending'
    STATUS_RESOLVED = 'resolved'
    STATUS_DISMISSED = 'dismissed'
    
    REASON_SPAM = 'spam'
    REASON_INAPPROPRIATE = 'inappropriate'
    REASON_VIOLATION = 'violation'
    REASON_OTHER = 'other'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.target_type = kwargs.get('target_type')
        self.target_id = kwargs.get('target_id')
        self.reason = kwargs.get('reason')
        self.reason_detail = kwargs.get('reason_detail')
        self.status = kwargs.get('status', self.STATUS_PENDING)
        self.handled_by = kwargs.get('handled_by')
        self.handled_at = kwargs.get('handled_at')
        self.handled_note = kwargs.get('handled_note')
        self.created_at = kwargs.get('created_at')
        self._reporter = None
        self._handler = None
        self._target_post = None
        self._target_comment = None
        self._target_user = None
    
    @staticmethod
    def create(user_id, target_type, target_id, reason, reason_detail=None):
        report_id = execute(
            '''INSERT INTO reports (user_id, target_type, target_id, reason, reason_detail)
               VALUES (%s, %s, %s, %s, %s) RETURNING id''',
            (user_id, target_type, target_id, reason, reason_detail)
        )
        return Report.get_by_id(report_id)
    
    @staticmethod
    def get_by_id(report_id):
        row = fetchone('SELECT * FROM reports WHERE id = %s', (report_id,))
        return Report(**row) if row else None
    
    @staticmethod
    def get_pending(limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM reports WHERE status = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (Report.STATUS_PENDING, limit, offset)
        )
        return [Report(**row) for row in rows]
    
    @staticmethod
    def get_for_admin(limit=20, offset=0, status=None):
        base_conditions = ['1=1']
        params = []
        
        if status:
            base_conditions.append('status = %s')
            params.append(status)
        
        where_clause = ' AND '.join(base_conditions)
        query = f'''SELECT * FROM reports WHERE {where_clause} 
                    ORDER BY created_at DESC LIMIT %s OFFSET %s'''
        params.extend([limit, offset])
        
        rows = fetchall(query, params)
        return [Report(**row) for row in rows]
    
    @staticmethod
    def count_for_admin(status=None):
        base_conditions = ['1=1']
        params = []
        
        if status:
            base_conditions.append('status = %s')
            params.append(status)
        
        where_clause = ' AND '.join(base_conditions)
        query = f'''SELECT COUNT(*) as count FROM reports WHERE {where_clause}'''
        
        row = fetchone(query, params)
        return row['count'] if row else 0
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM reports WHERE user_id = %s 
               ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
        return [Report(**row) for row in rows]
    
    def is_pending(self):
        return self.status == self.STATUS_PENDING
    
    def resolve(self, admin_id, note=None):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE reports SET status = %s, handled_by = %s, handled_at = %s, handled_note = %s 
               WHERE id = %s''',
            (self.STATUS_RESOLVED, admin_id, now, note, self.id)
        )
        self.status = self.STATUS_RESOLVED
        self.handled_by = admin_id
        self.handled_at = now
        self.handled_note = note
        return True
    
    def dismiss(self, admin_id, note=None):
        from datetime import datetime
        now = datetime.now()
        execute(
            '''UPDATE reports SET status = %s, handled_by = %s, handled_at = %s, handled_note = %s 
               WHERE id = %s''',
            (self.STATUS_DISMISSED, admin_id, now, note, self.id)
        )
        self.status = self.STATUS_DISMISSED
        self.handled_by = admin_id
        self.handled_at = now
        self.handled_note = note
        return True
    
    def get_reporter(self):
        if self._reporter is None and self.user_id:
            from models.user import User
            self._reporter = User.get_by_id(self.user_id)
        return self._reporter
    
    def get_handler(self):
        if self._handler is None and self.handled_by:
            from models.admin import Admin
            self._handler = Admin.get_by_id(self.handled_by)
        return self._handler
    
    def get_target_post(self):
        if self.target_type == self.TYPE_POST and self._target_post is None:
            from models.post import Post
            self._target_post = Post.get_by_id(self.target_id)
        return self._target_post
    
    def get_target_comment(self):
        if self.target_type == self.TYPE_COMMENT and self._target_comment is None:
            from models.comment import Comment
            self._target_comment = Comment.get_by_id(self.target_id)
        return self._target_comment
    
    def get_target_user(self):
        if self.target_type == self.TYPE_USER and self._target_user is None:
            from models.user import User
            self._target_user = User.get_by_id(self.target_id)
        return self._target_user
    
    def get_reason_name(self):
        reason_names = {
            self.REASON_SPAM: '垃圾广告',
            self.REASON_INAPPROPRIATE: '不适内容',
            self.REASON_VIOLATION: '违规内容',
            self.REASON_OTHER: '其他'
        }
        return reason_names.get(self.reason, '未知原因')
    
    def get_status_name(self):
        status_names = {
            self.STATUS_PENDING: '待处理',
            self.STATUS_RESOLVED: '已处理',
            self.STATUS_DISMISSED: '已驳回'
        }
        return status_names.get(self.status, '未知状态')
    
    def to_dict(self, include_reporter=False, include_handler=False, include_target=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'reason_name': self.get_reason_name(),
            'reason_detail': self.reason_detail,
            'status': self.status,
            'status_name': self.get_status_name(),
            'handled_by': self.handled_by,
            'handled_at': self.handled_at,
            'handled_note': self.handled_note,
            'created_at': self.created_at
        }
        
        if include_reporter:
            reporter = self.get_reporter()
            if reporter:
                data['reporter'] = {
                    'id': reporter.id,
                    'username': reporter.username,
                    'avatar': reporter.avatar
                }
        
        if include_handler:
            handler = self.get_handler()
            if handler:
                data['handler'] = {
                    'id': handler.id,
                    'username': handler.username
                }
        
        if include_target:
            if self.target_type == self.TYPE_POST:
                post = self.get_target_post()
                if post:
                    data['target'] = {
                        'type': 'post',
                        'id': post.id,
                        'title': post.title,
                        'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                        'is_hidden': post.is_hidden()
                    }
            elif self.target_type == self.TYPE_COMMENT:
                comment = self.get_target_comment()
                if comment:
                    data['target'] = {
                        'type': 'comment',
                        'id': comment.id,
                        'content': comment.content,
                        'post_id': comment.post_id
                    }
            elif self.target_type == self.TYPE_USER:
                user = self.get_target_user()
                if user:
                    data['target'] = {
                        'type': 'user',
                        'id': user.id,
                        'username': user.username,
                        'avatar': user.avatar,
                        'is_banned': user.is_banned if hasattr(user, 'is_banned') else False
                    }
        
        return data
