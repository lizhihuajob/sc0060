import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-2024')
    ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', 'admin-dev-secret-key-2024')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = '/tmp/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
    
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'appdb')
    DATABASE_USER = os.getenv('DATABASE_USER', 'appuser')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'apppassword')
    
    USER_LEVELS = {
        'bronze': {'name': '青铜', 'posts_limit': 2, 'price': 0},
        'silver': {'name': '白银', 'posts_limit': 4, 'price': 10},
        'gold': {'name': '黄金', 'posts_limit': 8, 'price': 30},
        'black': {'name': '黑金', 'posts_limit': 16, 'price': 100},
        'diamond': {'name': '钻石', 'posts_limit': 32, 'price': 300}
    }
    
    PIN_CONFIG = {
        'price': 20,
        'duration_days': 7,
        'max_count': 3
    }
    
    POINTS_CONFIG = {
        'daily_checkin_points': 10,
        'continuous_bonus_base': 5,
        'max_continuous_days': 7,
        'points_to_balance_rate': 100,
        'points_to_posts_rate': 50,
        'balance_per_exchange': 1,
        'posts_per_exchange': 1
    }
    
    INVITE_CONFIG = {
        'invite_reward_balance': 5,
        'invited_new_user_bonus': 10,
        'invite_code_length': 8
    }
    
    VIEW_PERMISSIONS = {
        'all': '所有用户',
        'registered': '平台注册者',
        'silver_above': '白银以上',
        'gold_above': '黄金以上'
    }
    
    ADMIN_ROLES = {
        'super_admin': '超级管理员',
        'admin': '管理员'
    }
    
    POST_STATUSES = {
        'active': '正常',
        'hidden': '已下架'
    }
    
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3002',
        'http://localhost:3008',
        'http://localhost:3009',
        'http://localhost:5002'
    ]
