from database import execute, fetchone, fetchall
from datetime import datetime
import json

class Notification:
    TYPE_FOLLOW = 'follow'
    TYPE_PIN = 'pin'
    TYPE_PIN_EXPIRING = 'pin_expiring'
    TYPE_MEMBERSHIP_EXPIRING = 'membership_expiring'
    TYPE_NEW_POST = 'new_post'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.type = kwargs.get('type')
        self.title = kwargs.get('title')
        self.content = kwargs.get('content')
        self.data = kwargs.get('data', '{}')
        self.is_read = kwargs.get('is_read', 0)
        self.created_at = kwargs.get('created_at')
    
    @staticmethod
    def create(user_id, notification_type, title, content, data=None):
        now = datetime.now()
        data_json = json.dumps(data) if data else '{}'
        notification_id = execute(
            '''INSERT INTO notifications (user_id, type, title, content, data, is_read, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
            (user_id, notification_type, title, content, data_json, 0, now)
        )
        return Notification.get_by_id(notification_id)
    
    @staticmethod
    def get_by_id(notification_id):
        row = fetchone('SELECT * FROM notifications WHERE id = %s', (notification_id,))
        return Notification(**row) if row else None
    
    @staticmethod
    def get_by_user(user_id, limit=20, offset=0, include_read=True):
        if include_read:
            rows = fetchall(
                '''SELECT * FROM notifications 
                   WHERE user_id = %s 
                   ORDER BY created_at DESC 
                   LIMIT %s OFFSET %s''',
                (user_id, limit, offset)
            )
        else:
            rows = fetchall(
                '''SELECT * FROM notifications 
                   WHERE user_id = %s AND is_read = 0 
                   ORDER BY created_at DESC 
                   LIMIT %s OFFSET %s''',
                (user_id, limit, offset)
            )
        return [Notification(**row) for row in rows] if rows else []
    
    @staticmethod
    def count_unread(user_id):
        row = fetchone(
            'SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = 0',
            (user_id,)
        )
        return row['count'] if row else 0
    
    @staticmethod
    def mark_as_read(notification_id):
        execute(
            'UPDATE notifications SET is_read = 1 WHERE id = %s',
            (notification_id,)
        )
        return True
    
    @staticmethod
    def mark_all_as_read(user_id):
        execute(
            'UPDATE notifications SET is_read = 1 WHERE user_id = %s',
            (user_id,)
        )
        return True
    
    def mark_read(self):
        Notification.mark_as_read(self.id)
        self.is_read = 1
        return True
    
    def delete(self):
        execute('DELETE FROM notifications WHERE id = %s', (self.id,))
        return True
    
    @staticmethod
    def notify_follow(follower, following):
        Notification.create(
            user_id=following.id,
            notification_type=Notification.TYPE_FOLLOW,
            title='新的关注',
            content=f'{follower.username} 关注了您',
            data={'follower_id': follower.id, 'follower_username': follower.username}
        )
    
    @staticmethod
    def notify_pin(post, is_expiring=False):
        if is_expiring:
            Notification.create(
                user_id=post.user_id,
                notification_type=Notification.TYPE_PIN_EXPIRING,
                title='置顶即将到期',
                content=f'您的公告「{post.title}」置顶即将到期',
                data={'post_id': post.id, 'post_title': post.title}
            )
        else:
            Notification.create(
                user_id=post.user_id,
                notification_type=Notification.TYPE_PIN,
                title='公告已置顶',
                content=f'您的公告「{post.title}」已成功置顶',
                data={'post_id': post.id, 'post_title': post.title}
            )
    
    @staticmethod
    def notify_new_post(post, follower_ids):
        for follower_id in follower_ids:
            Notification.create(
                user_id=follower_id,
                notification_type=Notification.TYPE_NEW_POST,
                title='关注用户发布新公告',
                content=f'{post.get_author().username} 发布了新公告：{post.title}',
                data={'post_id': post.id, 'post_title': post.title, 'author_id': post.user_id}
            )
    
    def get_data(self):
        try:
            return json.loads(self.data)
        except:
            return {}
    
    def get_type_name(self):
        type_names = {
            self.TYPE_FOLLOW: '关注',
            self.TYPE_PIN: '置顶',
            self.TYPE_PIN_EXPIRING: '置顶到期',
            self.TYPE_MEMBERSHIP_EXPIRING: '会员到期',
            self.TYPE_NEW_POST: '新公告'
        }
        return type_names.get(self.type, '其他')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'type_name': self.get_type_name(),
            'title': self.title,
            'content': self.content,
            'data': self.get_data(),
            'is_read': self.is_read,
            'created_at': self.created_at
        }
