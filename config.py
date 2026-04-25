import os
import secrets

class Config:
    SECRET_KEY = secrets.token_hex(32)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = '/tmp/app.db'
    UPLOAD_FOLDER = '/tmp/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    USER_LEVELS = {
        'bronze': {'name': '青铜', 'posts_limit': 2, 'price': 0},
        'silver': {'name': '白银', 'posts_limit': 4, 'price': 10},
        'gold': {'name': '黄金', 'posts_limit': 8, 'price': 30},
        'black': {'name': '黑金', 'posts_limit': 16, 'price': 100},
        'diamond': {'name': '钻石', 'posts_limit': 32, 'price': 300}
    }
    
    VIEW_PERMISSIONS = {
        'all': '所有用户',
        'registered': '平台注册者',
        'silver_above': '白银以上',
        'gold_above': '黄金以上'
    }
