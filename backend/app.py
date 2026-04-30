import os
import uuid
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from config import Config

from init_db import init_database
init_database()

from models import User, Post, Transaction, Comment, Favorite

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
        'view_permissions': Config.VIEW_PERMISSIONS,
        'pin_config': Config.PIN_CONFIG
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'user': user.to_dict()})
    return jsonify({'success': False, 'message': '未登录'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
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
    session.pop('user_id', None)
    session['user_id'] = user.id
    
    return jsonify({
        'success': True,
        'message': '注册成功！欢迎加入',
        'user': user.to_dict()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    user = User.get_by_username(username)
    
    if user and user.check_password(password):
        session.pop('user_id', None)
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
    
    keyword = request.args.get('keyword', '').strip()
    post_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort', 'latest')
    
    current_user = get_current_user()
    
    if not keyword and post_type == 'all' and sort_by == 'latest':
        posts = Post.get_visible_posts(current_user, limit=per_page, offset=offset)
    else:
        search_type = None if post_type == 'all' else post_type
        posts = Post.search_posts(
            current_user=current_user,
            keyword=keyword if keyword else None,
            post_type=search_type,
            sort_by=sort_by,
            limit=per_page,
            offset=offset
        )
    
    favorited_ids = []
    if current_user:
        favorited_ids = Favorite.get_favorited_post_ids(current_user.id)
    
    posts_data = []
    for post in posts:
        post_dict = post.to_dict(include_author=True)
        post_dict['is_favorited'] = post.id in favorited_ids
        posts_data.append(post_dict)
    
    return jsonify({
        'success': True,
        'posts': posts_data,
        'page': page,
        'per_page': per_page,
        'has_more': len(posts) >= per_page
    })

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    current_user = get_current_user()
    if not post.is_visible_to(current_user):
        return jsonify({'success': False, 'message': '您没有权限查看该公告'}), 403
    
    post.increment_views()
    comments = Comment.get_by_post(post_id)
    comments_count = Comment.count_by_post(post_id)
    
    post_dict = post.to_dict(include_author=True)
    if current_user:
        post_dict['is_favorited'] = Favorite.is_favorited(current_user.id, post_id)
    else:
        post_dict['is_favorited'] = False
    
    return jsonify({
        'success': True,
        'post': post_dict,
        'comments': [c.to_dict(include_author=True) for c in comments],
        'comments_count': comments_count
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

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    user = get_current_user()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if not post.is_owned_by(user):
        return jsonify({'success': False, 'message': '您没有权限删除该公告'}), 403
    
    post.delete()
    
    return jsonify({
        'success': True,
        'message': '删除成功'
    })

@app.route('/api/posts/pinned', methods=['GET'])
def get_pinned_posts():
    current_user = get_current_user()
    limit = request.args.get('limit', 3, type=int)
    
    posts = Post.get_active_pinned_posts(current_user, limit=limit)
    
    favorited_ids = []
    if current_user:
        favorited_ids = Favorite.get_favorited_post_ids(current_user.id)
    
    posts_data = []
    for post in posts:
        post_dict = post.to_dict(include_author=True)
        post_dict['is_favorited'] = post.id in favorited_ids
        posts_data.append(post_dict)
    
    return jsonify({
        'success': True,
        'posts': posts_data,
        'config': Config.PIN_CONFIG
    })

@app.route('/api/posts/<int:post_id>/pin', methods=['POST'])
@login_required
def pin_post(post_id):
    user = get_current_user()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if not post.is_owned_by(user):
        return jsonify({'success': False, 'message': '您没有权限操作该公告'}), 403
    
    if post.is_pinned:
        return jsonify({'success': False, 'message': '该公告已置顶'}), 400
    
    pin_count = Post.get_pinned_count()
    if pin_count >= Config.PIN_CONFIG['max_count']:
        return jsonify({
            'success': False, 
            'message': f'置顶位置已满，最多只能同时有 {Config.PIN_CONFIG["max_count"]} 条置顶消息'
        }), 400
    
    pin_price = Config.PIN_CONFIG['price']
    if user.balance < pin_price:
        return jsonify({
            'success': False, 
            'message': f'余额不足，置顶需要 ¥{pin_price}，当前余额 ¥{user.balance}'
        }), 400
    
    user.add_balance(-pin_price)
    Transaction.create(
        user.id,
        -pin_price,
        Transaction.TYPE_UPGRADE,
        f'置顶公告「{post.title[:20]}...」，有效期{Config.PIN_CONFIG["duration_days"]}天'
    )
    
    post.pin(duration_days=Config.PIN_CONFIG['duration_days'])
    
    return jsonify({
        'success': True,
        'message': f'置顶成功！有效期{Config.PIN_CONFIG["duration_days"]}天',
        'post': post.to_dict(include_author=True),
        'user': user.to_dict()
    })

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    current_user = get_current_user()
    if not post.is_visible_to(current_user):
        return jsonify({'success': False, 'message': '您没有权限查看该公告'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    comments = Comment.get_by_post(post_id, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'comments': [c.to_dict(include_author=True) for c in comments],
        'page': page,
        'per_page': per_page,
        'has_more': len(comments) >= per_page
    })

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def create_comment(post_id):
    user = get_current_user()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if not post.is_visible_to(user):
        return jsonify({'success': False, 'message': '您没有权限查看该公告'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'success': False, 'message': '留言内容不能为空'}), 400
    
    comment = Comment.create(post_id, user.id, content)
    
    return jsonify({
        'success': True,
        'message': '留言成功',
        'comment': comment.to_dict(include_author=True)
    })

@app.route('/api/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(post_id, comment_id):
    user = get_current_user()
    comment = Comment.get_by_id(comment_id)
    
    if not comment:
        return jsonify({'success': False, 'message': '该留言不存在'}), 404
    
    if comment.post_id != post_id:
        return jsonify({'success': False, 'message': '参数错误'}), 400
    
    if not comment.is_owned_by(user):
        return jsonify({'success': False, 'message': '您没有权限删除该留言'}), 403
    
    comment.delete()
    
    return jsonify({
        'success': True,
        'message': '留言已删除'
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

@app.route('/api/user/avatar', methods=['POST'])
@login_required
def upload_avatar():
    user = get_current_user()
    
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        user.update_avatar(unique_filename)
        
        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'avatar': unique_filename,
            'user': user.to_dict()
        })
    
    return jsonify({'success': False, 'message': '文件类型不支持'}), 400

@app.route('/api/user/password', methods=['PUT'])
@login_required
def change_password():
    user = get_current_user()
    
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not old_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的新密码不一致'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度不能少于6位'}), 400
    
    if user.change_password(old_password, new_password):
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    else:
        return jsonify({'success': False, 'message': '原密码错误'}), 400

@app.route('/api/posts/<int:post_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(post_id):
    user = get_current_user()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if not post.is_visible_to(user):
        return jsonify({'success': False, 'message': '您没有权限收藏该公告'}), 403
    
    is_favorited = Favorite.toggle(user.id, post_id)
    
    return jsonify({
        'success': True,
        'is_favorited': is_favorited,
        'message': '已收藏' if is_favorited else '已取消收藏'
    })

@app.route('/api/user/favorites', methods=['GET'])
@login_required
def get_user_favorites():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    rows = Favorite.get_by_user(user.id, limit=per_page, offset=offset)
    
    posts_data = []
    for row in rows:
        post = Post(**row)
        post_dict = post.to_dict(include_author=True)
        post_dict['is_favorited'] = True
        post_dict['favorited_at'] = row.get('created_at')
        posts_data.append(post_dict)
    
    return jsonify({
        'success': True,
        'posts': posts_data,
        'page': page,
        'per_page': per_page,
        'has_more': len(posts_data) >= per_page
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
