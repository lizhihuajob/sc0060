from werkzeug.security import generate_password_hash, check_password_hash
from database import execute, fetchone, fetchall

class Admin:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.email = kwargs.get('email')
        self.role = kwargs.get('role', 'admin')
        self.is_active = kwargs.get('is_active', 1)
        self.last_login_at = kwargs.get('last_login_at')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @staticmethod
    def create(username, password, email=None, role='admin'):
        hashed_password = generate_password_hash(password)
        admin_id = execute(
            '''INSERT INTO admins (username, password, email, role) 
               VALUES (%s, %s, %s, %s) RETURNING id''',
            (username, hashed_password, email, role)
        )
        return Admin.get_by_id(admin_id)
    
    @staticmethod
    def get_by_id(admin_id):
        row = fetchone('SELECT * FROM admins WHERE id = %s', (admin_id,))
        return Admin(**row) if row else None
    
    @staticmethod
    def get_by_username(username):
        row = fetchone('SELECT * FROM admins WHERE username = %s', (username,))
        return Admin(**row) if row else None
    
    @staticmethod
    def get_all(limit=20, offset=0):
        rows = fetchall(
            '''SELECT * FROM admins ORDER BY created_at DESC LIMIT %s OFFSET %s''',
            (limit, offset)
        )
        return [Admin(**row) for row in rows]
    
    @staticmethod
    def count():
        row = fetchone('SELECT COUNT(*) as count FROM admins')
        return row['count'] if row else 0
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def update_last_login(self):
        from datetime import datetime
        now = datetime.now()
        execute(
            'UPDATE admins SET last_login_at = %s WHERE id = %s',
            (now, self.id)
        )
        self.last_login_at = now
        return True
    
    def update_profile(self, email=None, role=None):
        updates = []
        params = []
        
        if email is not None:
            updates.append('email = %s')
            params.append(email)
        
        if role is not None:
            updates.append('role = %s')
            params.append(role)
        
        if not updates:
            return False
        
        from datetime import datetime
        updates.append('updated_at = %s')
        params.append(datetime.now())
        params.append(self.id)
        
        set_clause = ', '.join(updates)
        execute(
            f'UPDATE admins SET {set_clause} WHERE id = %s',
            params
        )
        
        if email is not None:
            self.email = email
        if role is not None:
            self.role = role
        return True
    
    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            return False
        
        hashed_password = generate_password_hash(new_password)
        from datetime import datetime
        execute(
            '''UPDATE admins SET password = %s, updated_at = %s WHERE id = %s''',
            (hashed_password, datetime.now(), self.id)
        )
        self.password = hashed_password
        return True
    
    def deactivate(self):
        from datetime import datetime
        execute(
            '''UPDATE admins SET is_active = 0, updated_at = %s WHERE id = %s''',
            (datetime.now(), self.id)
        )
        self.is_active = 0
        return True
    
    def activate(self):
        from datetime import datetime
        execute(
            '''UPDATE admins SET is_active = 1, updated_at = %s WHERE id = %s''',
            (datetime.now(), self.id)
        )
        self.is_active = 1
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login_at': self.last_login_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
