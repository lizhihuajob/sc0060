import os
import uuid
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from config import Config

from init_db import init_database
init_database()

from models import User, Post, Transaction, Comment, Favorite, Report, Announcement, Tag, PostTag, CheckinRecord, PointsTransaction, InviteRecord

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
        
        user = User.get_by_id(session['user_id'])
        if user and user.is_banned_user():
            session.pop('user_id', None)
            return jsonify({'success': False, 'message': '您的账户已被封禁，请联系管理员'}), 403
        
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

@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.get_all(include_inactive=False)
    return jsonify({
        'success': True,
        'tags': [tag.to_dict() for tag in tags]
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'user': user.to_dict()})
    return jsonify({'success': False, 'message': '未登录'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    email = data.get('email', '').strip()
    invite_code = data.get('invite_code', '').strip() or None
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400
    
    if User.get_by_username(username):
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    if invite_code:
        inviter = User.get_by_invite_code(invite_code)
        if not inviter:
            return jsonify({'success': False, 'message': '邀请码无效'}), 400
    
    user = User.create(username, password, email, invite_code)
    
    if invite_code:
        inviter = User.get_by_invite_code(invite_code)
        if inviter:
            reward_amount = Config.INVITE_CONFIG.get('invite_reward_balance', 5)
            InviteRecord.create(
                inviter_id=inviter.id,
                invited_user_id=user.id,
                reward_amount=reward_amount
            )
    
    session.pop('user_id', None)
    session['user_id'] = user.id
    session.permanent = True
    
    return jsonify({
        'success': True,
        'message': '注册成功！欢迎加入',
        'user': user.to_dict()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    user = User.get_by_username(username)
    
    if user and user.check_password(password):
        session.pop('user_id', None)
        session['user_id'] = user.id
        session.permanent = True
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
    tag_id = request.args.get('tag_id', None, type=int)
    
    current_user = get_current_user()
    
    if not keyword and post_type == 'all' and sort_by == 'latest' and not tag_id:
        posts = Post.get_visible_posts(current_user, limit=per_page, offset=offset)
    else:
        search_type = None if post_type == 'all' else post_type
        posts = Post.search_posts(
            current_user=current_user,
            keyword=keyword if keyword else None,
            post_type=search_type,
            sort_by=sort_by,
            tag_id=tag_id,
            limit=per_page,
            offset=offset
        )
    
    favorited_ids = []
    if current_user:
        favorited_ids = Favorite.get_favorited_post_ids(current_user.id)
    
    posts_data = []
    for post in posts:
        post_dict = post.to_dict(include_author=True, include_tags=True)
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
    comments = Comment.get_by_post_with_replies(post_id, limit=20)
    comments_count = Comment.count_by_post(post_id)
    
    post_dict = post.to_dict(include_author=True, include_tags=True)
    if current_user:
        post_dict['is_favorited'] = Favorite.is_favorited(current_user.id, post_id)
    else:
        post_dict['is_favorited'] = False
    
    return jsonify({
        'success': True,
        'post': post_dict,
        'comments': [c.to_dict(include_author=True, include_replies=True) for c in comments],
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
        'posts': [post.to_dict(include_author=True, include_tags=True) for post in posts],
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
    
    tag_ids_str = request.form.get('tag_ids', '')
    tag_ids = []
    if tag_ids_str:
        try:
            tag_ids = [int(tid.strip()) for tid in tag_ids_str.split(',') if tid.strip()]
        except:
            tag_ids = []
    
    valid_tag_ids = []
    for tag_id in tag_ids:
        tag = Tag.get_by_id(tag_id)
        if tag and tag.is_active:
            valid_tag_ids.append(tag_id)
    
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
    
    if valid_tag_ids:
        PostTag.add_tags_to_post(post.id, valid_tag_ids)
    
    user.increment_posts_count()
    
    return jsonify({
        'success': True,
        'message': '任务发布成功！' if is_task else '公告发布成功！',
        'post': post.to_dict(include_author=True, include_tags=True)
    })

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    from models import EditLog
    
    user = get_current_user()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '该公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告已被下架，无法编辑'}), 400
    
    if not post.is_owned_by(user):
        return jsonify({'success': False, 'message': '您没有权限编辑该公告'}), 403
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    view_permission = request.form.get('view_permission')
    is_task = request.form.get('is_task')
    edit_reason = request.form.get('edit_reason', '').strip()
    
    tag_ids_str = request.form.get('tag_ids', None)
    tags_updated = False
    if tag_ids_str is not None:
        tags_updated = True
        try:
            tag_ids = [int(tid.strip()) for tid in tag_ids_str.split(',') if tid.strip()]
        except:
            tag_ids = []
        
        valid_tag_ids = []
        for tag_id in tag_ids:
            tag = Tag.get_by_id(tag_id)
            if tag and tag.is_active:
                valid_tag_ids.append(tag_id)
    
    updates = {}
    if title:
        updates['title'] = title
    if content:
        updates['content'] = content
    if view_permission is not None:
        updates['view_permission'] = view_permission
    if is_task is not None:
        try:
            updates['is_task'] = int(is_task)
        except ValueError:
            pass
    
    old_data = post.get_old_data()
    
    new_images = None
    if 'images' in request.files:
        files = request.files.getlist('images')
        if files and files[0].filename:
            new_images = []
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    new_images.append(unique_filename)
    
    if new_images is not None:
        updates['images'] = new_images
    
    if not updates and not tags_updated:
        return jsonify({'success': False, 'message': '没有需要更新的内容'}), 400
    
    if updates:
        post.update(**updates)
    
    if tags_updated:
        PostTag.set_post_tags(post.id, valid_tag_ids)
    
    new_data = {
        'title': updates.get('title', old_data['title']),
        'content': updates.get('content', old_data['content']),
        'view_permission': updates.get('view_permission', old_data['view_permission']),
        'is_task': updates.get('is_task', old_data['is_task'])
    }
    
    EditLog.create(
        post_id=post.id,
        user_id=user.id,
        old_data=old_data,
        new_data=new_data,
        edit_reason=edit_reason if edit_reason else None
    )
    
    return jsonify({
        'success': True,
        'message': '更新成功！',
        'post': post.to_dict(include_author=True, include_tags=True)
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
    
    comments = Comment.get_by_post_with_replies(post_id, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'comments': [c.to_dict(include_author=True, include_replies=True) for c in comments],
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
    
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    reply_to_user_id = data.get('reply_to_user_id')
    
    if not content:
        return jsonify({'success': False, 'message': '留言内容不能为空'}), 400
    
    if parent_id:
        parent_comment = Comment.get_by_id(parent_id)
        if not parent_comment or parent_comment.post_id != post_id:
            return jsonify({'success': False, 'message': '回复的评论不存在'}), 400
    
    comment = Comment.create(
        post_id, 
        user.id, 
        content, 
        parent_id=parent_id,
        reply_to_user_id=reply_to_user_id
    )
    
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
    from models import EditLog
    
    user = get_current_user()
    transactions = Transaction.get_by_user(user.id, limit=10)
    edit_logs = EditLog.get_by_user(user.id, limit=10)
    edit_logs_count = EditLog.count_by_user(user.id)
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'transactions': [t.to_dict() for t in transactions],
        'edit_logs': [log.to_dict(include_post=True) for log in edit_logs],
        'edit_logs_count': edit_logs_count
    })

@app.route('/api/user/edit-logs', methods=['GET'])
@login_required
def get_user_edit_logs():
    from models import EditLog
    
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    edit_logs = EditLog.get_by_user(user.id, limit=per_page, offset=offset)
    total = EditLog.count_by_user(user.id)
    
    return jsonify({
        'success': True,
        'edit_logs': [log.to_dict(include_post=True) for log in edit_logs],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/user/upgrade', methods=['POST'])
@login_required
def upgrade():
    user = get_current_user()
    
    data = request.get_json() or {}
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
    
    data = request.get_json() or {}
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
    
    data = request.get_json() or {}
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

@app.route('/api/user/checkin', methods=['POST'])
@login_required
def checkin():
    user = get_current_user()
    
    result, error = user.checkin()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': '签到成功',
        'data': result,
        'user': user.to_dict()
    })

@app.route('/api/user/checkin/status', methods=['GET'])
@login_required
def get_checkin_status():
    from datetime import date
    
    user = get_current_user()
    
    today = date.today()
    has_checked_in = CheckinRecord.check_today(user.id)
    continuous_days = CheckinRecord.count_continuous_days(user.id, today)
    
    return jsonify({
        'success': True,
        'data': {
            'has_checked_in': has_checked_in,
            'continuous_days': continuous_days,
            'points': user.points,
            'config': Config.POINTS_CONFIG
        }
    })

@app.route('/api/user/checkin/history', methods=['GET'])
@login_required
def get_checkin_history():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    offset = (page - 1) * per_page
    
    records = CheckinRecord.get_by_user(user.id, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'records': [r.to_dict() for r in records],
        'page': page,
        'per_page': per_page
    })

@app.route('/api/user/points/transactions', methods=['GET'])
@login_required
def get_points_transactions():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    transactions = PointsTransaction.get_by_user(user.id, limit=per_page, offset=offset)
    total = PointsTransaction.count_by_user(user.id)
    
    return jsonify({
        'success': True,
        'transactions': [t.to_dict() for t in transactions],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/user/points/exchange/balance', methods=['POST'])
@login_required
def exchange_points_to_balance():
    user = get_current_user()
    data = request.get_json() or {}
    exchange_count = data.get('count', 1)
    
    try:
        exchange_count = int(exchange_count)
        if exchange_count < 1:
            raise ValueError()
    except:
        return jsonify({'success': False, 'message': '请输入有效的兑换数量'}), 400
    
    success, message = user.exchange_points_to_balance(exchange_count)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
    
    return jsonify({
        'success': True,
        'message': message,
        'user': user.to_dict()
    })

@app.route('/api/user/points/exchange/posts', methods=['POST'])
@login_required
def exchange_points_to_posts():
    user = get_current_user()
    data = request.get_json() or {}
    exchange_count = data.get('count', 1)
    
    try:
        exchange_count = int(exchange_count)
        if exchange_count < 1:
            raise ValueError()
    except:
        return jsonify({'success': False, 'message': '请输入有效的兑换数量'}), 400
    
    success, message = user.exchange_points_to_posts(exchange_count)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
    
    return jsonify({
        'success': True,
        'message': message,
        'user': user.to_dict()
    })

@app.route('/api/user/invite', methods=['GET'])
@login_required
def get_invite_info():
    user = get_current_user()
    
    invite_stats = user.get_invite_stats()
    
    return jsonify({
        'success': True,
        'data': invite_stats,
        'config': Config.INVITE_CONFIG
    })

@app.route('/api/user/invite/records', methods=['GET'])
@login_required
def get_invite_records():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    records = InviteRecord.get_by_inviter(user.id, limit=per_page, offset=offset)
    total = InviteRecord.count_by_inviter(user.id)
    
    return jsonify({
        'success': True,
        'records': [r.to_dict(include_invited_user=True) for r in records],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/user/invite/claim', methods=['POST'])
@login_required
def claim_invite_rewards():
    user = get_current_user()
    data = request.get_json() or {}
    record_id = data.get('record_id')
    
    if not record_id:
        unclaimed_records = InviteRecord.get_by_inviter(user.id, limit=100)
        total_reward = 0
        claimed_count = 0
        
        for record in unclaimed_records:
            if record.reward_claimed == 0:
                reward = record.reward_amount or Config.INVITE_CONFIG.get('invite_reward_balance', 5)
                user.add_balance(reward)
                Transaction.create(
                    user.id,
                    reward,
                    Transaction.TYPE_INVITE_REWARD,
                    f'邀请奖励：邀请用户「{User.get_by_id(record.invited_user_id).username if User.get_by_id(record.invited_user_id) else "未知"}」注册'
                )
                record.claim_reward()
                total_reward += reward
                claimed_count += 1
        
        if claimed_count == 0:
            return jsonify({'success': False, 'message': '没有可领取的奖励'}), 400
        
        return jsonify({
            'success': True,
            'message': f'成功领取 {claimed_count} 笔奖励，共 {total_reward} 元',
            'user': user.to_dict()
        })
    
    record = InviteRecord.get_by_id(record_id)
    if not record or record.inviter_id != user.id:
        return jsonify({'success': False, 'message': '奖励记录不存在'}), 404
    
    if record.reward_claimed == 1:
        return jsonify({'success': False, 'message': '该奖励已领取'}), 400
    
    reward = record.reward_amount or Config.INVITE_CONFIG.get('invite_reward_balance', 5)
    user.add_balance(reward)
    Transaction.create(
        user.id,
        reward,
        Transaction.TYPE_INVITE_REWARD,
        f'邀请奖励：邀请用户注册'
    )
    record.claim_reward()
    
    return jsonify({
        'success': True,
        'message': f'领取成功，获得 {reward} 元',
        'user': user.to_dict()
    })

@app.route('/api/share/link', methods=['GET'])
@login_required
def get_share_link():
    from flask import request as flask_request
    
    user = get_current_user()
    share_type = request.args.get('type', 'invite')
    target_id = request.args.get('id')
    
    host_url = flask_request.host_url.rstrip('/')
    
    share_info = {}
    
    if share_type == 'invite':
        share_info = {
            'type': 'invite',
            'title': f'来自 {user.username} 的邀请',
            'description': '加入我们，注册即送积分奖励！',
            'url': f'{host_url}/register?invite_code={user.invite_code}',
            'invite_code': user.invite_code
        }
    elif share_type == 'post' and target_id:
        post = Post.get_by_id(int(target_id))
        if post and not post.is_hidden():
            share_info = {
                'type': 'post',
                'title': post.title,
                'description': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'url': f'{host_url}/post/{post.id}'
            }
    elif share_type == 'announcement' and target_id:
        from models import Announcement
        announcement = Announcement.get_by_id(int(target_id))
        if announcement and announcement.is_active():
            share_info = {
                'type': 'announcement',
                'title': announcement.title,
                'description': announcement.content[:100] + '...' if len(announcement.content) > 100 else announcement.content,
                'url': f'{host_url}/announcement/{announcement.id}'
            }
    
    if not share_info:
        return jsonify({'success': False, 'message': '分享内容不存在'}), 404
    
    return jsonify({
        'success': True,
        'share': share_info
    })

@app.route('/api/share/qrcode', methods=['GET'])
@login_required
def generate_qrcode():
    import io
    import base64
    
    url = request.args.get('url')
    if not url:
        return jsonify({'success': False, 'message': '缺少URL参数'}), 400
    
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_L
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'qrcode': f'data:image/png;base64,{img_base64}',
            'url': url
        })
    except ImportError:
        return jsonify({
            'success': True,
            'qrcode': None,
            'message': '请安装 qrcode 库以生成二维码',
            'url': url
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成二维码失败: {str(e)}'}), 500

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

@app.route('/api/reports', methods=['POST'])
@login_required
def create_report():
    user = get_current_user()
    data = request.get_json() or {}
    
    target_type = data.get('target_type', '').strip()
    target_id = data.get('target_id')
    reason = data.get('reason', '').strip() or data.get('reason_type', '').strip()
    reason_detail = data.get('reason_detail', '').strip() or data.get('description', '').strip()
    
    valid_target_types = [Report.TYPE_POST, Report.TYPE_COMMENT, Report.TYPE_USER]
    if target_type not in valid_target_types:
        return jsonify({'success': False, 'message': '无效的举报类型'}), 400
    
    if not target_id:
        return jsonify({'success': False, 'message': '请指定举报目标'}), 400
    
    valid_reasons = [Report.REASON_SPAM, Report.REASON_INAPPROPRIATE, Report.REASON_VIOLATION, Report.REASON_OTHER]
    if reason not in valid_reasons:
        return jsonify({'success': False, 'message': '无效的举报原因'}), 400
    
    if target_type == Report.TYPE_POST:
        post = Post.get_by_id(target_id)
        if not post:
            return jsonify({'success': False, 'message': '举报的帖子不存在'}), 404
    
    elif target_type == Report.TYPE_COMMENT:
        comment = Comment.get_by_id(target_id)
        if not comment:
            return jsonify({'success': False, 'message': '举报的评论不存在'}), 404
    
    elif target_type == Report.TYPE_USER:
        target_user = User.get_by_id(target_id)
        if not target_user:
            return jsonify({'success': False, 'message': '举报的用户不存在'}), 404
        if target_user.id == user.id:
            return jsonify({'success': False, 'message': '不能举报自己'}), 400
    
    report = Report.create(
        user_id=user.id,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        reason_detail=reason_detail if reason_detail else None
    )
    
    return jsonify({
        'success': True,
        'message': '举报已提交，感谢您的反馈',
        'report': report.to_dict()
    })

@app.route('/api/reports/my', methods=['GET'])
@login_required
def get_my_reports():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    reports = Report.get_by_user(user.id, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'reports': [r.to_dict() for r in reports],
        'page': page,
        'per_page': per_page,
        'has_more': len(reports) >= per_page
    })

@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    current_user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    announcements = Announcement.get_active(current_user, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'announcements': [a.to_dict() for a in announcements],
        'page': page,
        'per_page': per_page,
        'has_more': len(announcements) >= per_page
    })

@app.route('/api/announcements/pinned', methods=['GET'])
def get_pinned_announcements():
    current_user = get_current_user()
    limit = request.args.get('limit', 3, type=int)
    
    announcements = Announcement.get_pinned(current_user, limit=limit)
    
    return jsonify({
        'success': True,
        'announcements': [a.to_dict() for a in announcements]
    })

@app.route('/api/announcements/<int:announcement_id>', methods=['GET'])
def get_announcement_detail(announcement_id):
    announcement = Announcement.get_by_id(announcement_id)
    
    if not announcement or not announcement.is_active():
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    return jsonify({
        'success': True,
        'announcement': announcement.to_dict(include_admin=True)
    })

@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message': '公告平台后端服务运行中',
        'info': '请通过前端端口访问：http://localhost:3008',
        'api_base': '/api'
    })

@app.route('/health')
def health_check():
    return jsonify({
        'success': True,
        'message': '服务运行正常',
        'service': 'main-backend',
        'port': 5000
    })

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': '接口不存在'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
