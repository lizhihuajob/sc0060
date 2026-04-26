import os
import uuid
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from config import Config

from init_db import init_database
init_database()

from models import User, Post, Transaction

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.get_by_id(session['user_id'])
    return None

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'user_levels': Config.USER_LEVELS,
        'view_permissions': Config.VIEW_PERMISSIONS
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'user': user.to_dict()})
    return jsonify({'success': False, 'message': '未登录'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    if 'user_id' in session:
        return jsonify({'success': False, 'message': '已登录'}), 400
    
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    email = data.get('email', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400
    
    if User.get_by_username(username):
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    user = User.create(username, password, email)
    session['user_id'] = user.id
    
    return jsonify({
        'success': True,
        'message': '注册成功！欢迎加入',
        'user': user.to_dict()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    if 'user_id' in session:
        return jsonify({'success': False, 'message': '已登录'}), 400
    
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    user = User.get_by_username(username)
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({
            'success': True,
            'message': '登录成功！',
            'user': user.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': '已退出登录'})

@app.route('/api/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    current_user = get_current_user()
    posts = Post.get_visible_posts(current_user, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'posts': [post.to_dict(include_author=True) for post in posts],
        'page': page,
        'per_page': per_page,
        'has_more': len(posts) >= per_page
    })

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    current_user = get_current_user()
    if not post.is_visible_to(current_user):
        return jsonify({'success': False, 'message': '您没有权限查看该公告'}), 403
    
    return jsonify({
        'success': True,
        'post': post.to_dict(include_author=True)
    })

@app.route('/api/posts/my', methods=['GET'])
@login_required
def get_my_posts():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    posts = Post.get_by_user(user.id, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'posts': [post.to_dict(include_author=True) for post in posts],
        'page': page,
        'per_page': per_page,
        'has_more': len(posts) >= per_page
    })

@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    user = get_current_user()
    
    if not user.can_post():
        return jsonify({
            'success': False,
            'message': f'您的发布数量已达上限（{user.posts_count}/{user.get_posts_limit()}），请升级会员等级'
        }), 400
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    view_permission = request.form.get('view_permission', 'all')
    is_task = int(request.form.get('is_task', 0))
    
    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400
    
    images = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                images.append(unique_filename)
    
    post = Post.create(
        user_id=user.id,
        title=title,
        content=content,
        view_permission=view_permission,
        images=images if images else None,
        is_task=is_task
    )
    
    user.increment_posts_count()
    
    return jsonify({
        'success': True,
        'message': '任务发布成功！' if is_task else '公告发布成功！',
        'post': post.to_dict(include_author=True)
    })

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_profile():
    user = get_current_user()
    transactions = Transaction.get_by_user(user.id, limit=10)
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'transactions': [t.to_dict() for t in transactions]
    })

@app.route('/api/user/upgrade', methods=['POST'])
@login_required
def upgrade():
    user = get_current_user()
    
    data = request.get_json()
    target_level = data.get('level', '')
    
    if target_level not in Config.USER_LEVELS:
        return jsonify({'success': False, 'message': '无效的等级'}), 400
    
    level_info = Config.USER_LEVELS[target_level]
    current_level_order = list(Config.USER_LEVELS.keys())
    current_index = current_level_order.index(user.level)
    target_index = current_level_order.index(target_level)
    
    if target_index <= current_index:
        return jsonify({'success': False, 'message': '只能升级到更高等级'}), 400
    
    if user.balance < level_info['price']:
        return jsonify({'success': False, 'message': f'余额不足，需要 {level_info["price"]} 元'}), 400
    
    old_level_name = user.get_level_info()['name']
    if user.upgrade_level(target_level):
        Transaction.create(
            user.id,
            -level_info['price'],
            Transaction.TYPE_UPGRADE,
            f'从{old_level_name}升级到{level_info["name"]}'
        )
        return jsonify({
            'success': True,
            'message': f'升级成功！您现在是{level_info["name"]}会员',
            'user': user.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': '升级失败'}), 500

@app.route('/api/user/recharge', methods=['POST'])
@login_required
def recharge():
    user = get_current_user()
    
    data = request.get_json()
    amount = data.get('amount', 0)
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except:
        return jsonify({'success': False, 'message': '请输入有效的充值金额'}), 400
    
    user.add_balance(amount)
    Transaction.create(
        user.id,
        amount,
        Transaction.TYPE_RECHARGE,
        f'充值 {amount} 元'
    )
    
    return jsonify({
        'success': True,
        'message': f'充值成功！已到账 {amount} 元',
        'user': user.to_dict()
    })

@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': '接口不存在'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
