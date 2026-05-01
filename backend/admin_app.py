import os
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory, redirect, url_for
from flask_cors import CORS
from config import Config

from init_db import init_database
init_database()

from models import Admin, User, Post, Transaction, Tag, PostTag, Report, Announcement

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ADMIN_STATIC_FOLDER = os.path.join(BASE_DIR, 'admin_static')

admin_app = Flask(__name__, static_folder=ADMIN_STATIC_FOLDER)
admin_app.config.from_object(Config)
admin_app.config['SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'admin-secret-key-change-in-production')

CORS(admin_app, supports_credentials=True, origins=Config.CORS_ORIGINS)

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'success': False, 'message': '请先登录管理员账户'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_admin():
    if 'admin_id' in session:
        return Admin.get_by_id(session['admin_id'])
    return None

@admin_app.route('/api/admin/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'message': 'Admin service is running', 'port': 3009})

@admin_app.route('/api/admin/auth/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    admin = Admin.get_by_username(username)
    
    if not admin:
        admin_count = Admin.count()
        if admin_count == 0:
            default_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
            default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
            
            if username == default_username and password == default_password:
                admin = Admin.create(
                    username=default_username,
                    password=default_password,
                    email='admin@example.com',
                    role='super_admin'
                )
                session.pop('admin_id', None)
                session['admin_id'] = admin.id
                admin.update_last_login()
                return jsonify({
                    'success': True,
                    'message': '默认管理员登录成功！请及时修改密码',
                    'admin': admin.to_dict()
                })
        
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    if not admin.is_active:
        return jsonify({'success': False, 'message': '该管理员账户已被禁用'}), 403
    
    if admin.check_password(password):
        session.pop('admin_id', None)
        session['admin_id'] = admin.id
        admin.update_last_login()
        return jsonify({
            'success': True,
            'message': '登录成功！',
            'admin': admin.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@admin_app.route('/api/admin/auth/logout', methods=['POST'])
@admin_login_required
def admin_logout():
    session.pop('admin_id', None)
    return jsonify({'success': True, 'message': '已退出登录'})

@admin_app.route('/api/admin/auth/me', methods=['GET'])
@admin_login_required
def get_current_admin_info():
    admin = get_current_admin()
    if admin:
        return jsonify({'success': True, 'admin': admin.to_dict()})
    return jsonify({'success': False, 'message': '未登录'}), 401

@admin_app.route('/api/admin/profile', methods=['GET'])
@admin_login_required
def get_admin_profile():
    admin = get_current_admin()
    return jsonify({
        'success': True,
        'admin': admin.to_dict()
    })

@admin_app.route('/api/admin/profile', methods=['PUT'])
@admin_login_required
def update_admin_profile():
    admin = get_current_admin()
    data = request.get_json()
    
    email = data.get('email')
    
    updates = {}
    if email is not None:
        updates['email'] = email
    
    if not updates:
        return jsonify({'success': False, 'message': '没有需要更新的信息'}), 400
    
    admin.update_profile(**updates)
    
    return jsonify({
        'success': True,
        'message': '个人信息更新成功',
        'admin': admin.to_dict()
    })

@admin_app.route('/api/admin/password', methods=['PUT'])
@admin_login_required
def change_admin_password():
    admin = get_current_admin()
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
    
    if admin.change_password(old_password, new_password):
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    else:
        return jsonify({'success': False, 'message': '原密码错误'}), 400

@admin_app.route('/api/admin/users', methods=['GET'])
@admin_login_required
def get_users_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    level = request.args.get('level', '').strip()
    keyword = request.args.get('keyword', '').strip()
    
    level_filter = level if level else None
    keyword_filter = keyword if keyword else None
    
    users = User.get_all_for_admin(
        limit=per_page,
        offset=offset,
        level=level_filter,
        keyword=keyword_filter
    )
    
    total = User.count_for_admin(level=level_filter, keyword=keyword_filter)
    
    users_data = []
    for user in users:
        user_dict = user.to_dict(include_transactions_summary=True)
        users_data.append(user_dict)
    
    return jsonify({
        'success': True,
        'users': users_data,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })

@admin_app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_login_required
def get_user_detail(user_id):
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    transactions = Transaction.get_by_user(user_id, limit=20)
    
    user_dict = user.to_dict(include_transactions_summary=True)
    
    return jsonify({
        'success': True,
        'user': user_dict,
        'transactions': [t.to_dict() for t in transactions]
    })

@admin_app.route('/api/admin/users/stats', methods=['GET'])
@admin_login_required
def get_users_stats():
    total_users = User.count_for_admin()
    total_recharge = User.get_total_recharge()
    
    level_stats = {}
    for level_key in Config.USER_LEVELS.keys():
        count = User.count_for_admin(level=level_key)
        level_stats[level_key] = {
            'count': count,
            'name': Config.USER_LEVELS[level_key]['name']
        }
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'total_recharge': total_recharge,
            'level_distribution': level_stats
        }
    })

@admin_app.route('/api/admin/posts', methods=['GET'])
@admin_login_required
def get_posts_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    status = request.args.get('status', '').strip()
    keyword = request.args.get('keyword', '').strip()
    
    status_filter = status if status else None
    keyword_filter = keyword if keyword else None
    
    posts = Post.get_all_for_admin(
        limit=per_page,
        offset=offset,
        status=status_filter,
        keyword=keyword_filter
    )
    
    total = Post.count_for_admin(status=status_filter, keyword=keyword_filter)
    
    posts_data = []
    for post in posts:
        post_dict = post.to_dict(include_author=True, include_admin_info=True)
        posts_data.append(post_dict)
    
    return jsonify({
        'success': True,
        'posts': posts_data,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })

@admin_app.route('/api/admin/posts/<int:post_id>', methods=['GET'])
@admin_login_required
def get_post_detail(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    return jsonify({
        'success': True,
        'post': post.to_dict(include_author=True, include_admin_info=True)
    })

@admin_app.route('/api/admin/posts/<int:post_id>/hide', methods=['POST'])
@admin_login_required
def hide_post(post_id):
    admin = get_current_admin()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    if post.is_hidden():
        return jsonify({'success': False, 'message': '该公告已被下架'}), 400
    
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()
    
    post.hide(admin_id=admin.id, reason=reason if reason else None)
    
    return jsonify({
        'success': True,
        'message': '公告已下架',
        'post': post.to_dict(include_author=True, include_admin_info=True)
    })

@admin_app.route('/api/admin/posts/<int:post_id>/unhide', methods=['POST'])
@admin_login_required
def unhide_post(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    if not post.is_hidden():
        return jsonify({'success': False, 'message': '该公告未被下架'}), 400
    
    post.unhide()
    
    return jsonify({
        'success': True,
        'message': '公告已恢复',
        'post': post.to_dict(include_author=True, include_admin_info=True)
    })

@admin_app.route('/api/admin/posts/stats', methods=['GET'])
@admin_login_required
def get_posts_stats():
    total_posts = Post.count_for_admin()
    active_posts = Post.count_for_admin(status=Post.STATUS_ACTIVE)
    hidden_posts = Post.count_for_admin(status=Post.STATUS_HIDDEN)
    
    return jsonify({
        'success': True,
        'stats': {
            'total_posts': total_posts,
            'active_posts': active_posts,
            'hidden_posts': hidden_posts
        }
    })

@admin_app.route('/api/admin/tags', methods=['GET'])
@admin_login_required
def get_tags_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    keyword = request.args.get('keyword', '').strip()
    is_active = request.args.get('is_active', '')
    
    is_active_filter = None
    if is_active == '1':
        is_active_filter = True
    elif is_active == '0':
        is_active_filter = False
    
    keyword_filter = keyword if keyword else None
    
    tags = Tag.get_for_admin(
        limit=per_page,
        offset=offset,
        keyword=keyword_filter,
        is_active=is_active_filter
    )
    
    total = Tag.count_for_admin(
        keyword=keyword_filter,
        is_active=is_active_filter
    )
    
    tags_data = []
    for tag in tags:
        tag_dict = tag.to_dict(include_posts_count=True)
        tags_data.append(tag_dict)
    
    return jsonify({
        'success': True,
        'tags': tags_data,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })

@admin_app.route('/api/admin/tags/all', methods=['GET'])
@admin_login_required
def get_all_tags():
    tags = Tag.get_all(include_inactive=True)
    return jsonify({
        'success': True,
        'tags': [tag.to_dict() for tag in tags]
    })

@admin_app.route('/api/admin/tags/<int:tag_id>', methods=['GET'])
@admin_login_required
def get_tag_detail(tag_id):
    tag = Tag.get_by_id(tag_id)
    
    if not tag:
        return jsonify({'success': False, 'message': '标签不存在'}), 404
    
    tag_dict = tag.to_dict(include_posts_count=True)
    
    return jsonify({
        'success': True,
        'tag': tag_dict
    })

@admin_app.route('/api/admin/tags', methods=['POST'])
@admin_login_required
def create_tag():
    admin = get_current_admin()
    data = request.get_json()
    
    name = data.get('name', '').strip()
    slug = data.get('slug', '').strip()
    description = data.get('description', '').strip()
    color = data.get('color', '#0071e3')
    icon = data.get('icon', '').strip()
    sort_order = data.get('sort_order', 0)
    
    if not name:
        return jsonify({'success': False, 'message': '标签名称不能为空'}), 400
    
    if not slug:
        slug = name.lower().replace(' ', '-').replace('_', '-')
    
    existing_tag = Tag.get_by_slug(slug)
    if existing_tag:
        return jsonify({'success': False, 'message': '标签标识已存在，请使用其他标识'}), 400
    
    tag = Tag.create(
        name=name,
        slug=slug,
        description=description if description else None,
        color=color,
        icon=icon if icon else None,
        sort_order=sort_order
    )
    
    return jsonify({
        'success': True,
        'message': '标签创建成功',
        'tag': tag.to_dict()
    })

@admin_app.route('/api/admin/tags/<int:tag_id>', methods=['PUT'])
@admin_login_required
def update_tag(tag_id):
    admin = get_current_admin()
    tag = Tag.get_by_id(tag_id)
    
    if not tag:
        return jsonify({'success': False, 'message': '标签不存在'}), 404
    
    data = request.get_json()
    
    name = data.get('name')
    slug = data.get('slug')
    description = data.get('description')
    color = data.get('color')
    icon = data.get('icon')
    sort_order = data.get('sort_order')
    is_active = data.get('is_active')
    
    if slug is not None and slug != tag.slug:
        existing_tag = Tag.get_by_slug(slug)
        if existing_tag and existing_tag.id != tag_id:
            return jsonify({'success': False, 'message': '标签标识已存在'}), 400
    
    tag.update(
        name=name,
        slug=slug,
        description=description,
        color=color,
        icon=icon,
        sort_order=sort_order,
        is_active=is_active
    )
    
    return jsonify({
        'success': True,
        'message': '标签更新成功',
        'tag': tag.to_dict()
    })

@admin_app.route('/api/admin/tags/<int:tag_id>', methods=['DELETE'])
@admin_login_required
def delete_tag(tag_id):
    tag = Tag.get_by_id(tag_id)
    
    if not tag:
        return jsonify({'success': False, 'message': '标签不存在'}), 404
    
    posts_count = tag.get_posts_count()
    if posts_count > 0:
        return jsonify({
            'success': False, 
            'message': f'该标签下还有 {posts_count} 篇帖子，请先移除这些帖子的标签后再删除'
        }), 400
    
    tag.delete()
    
    return jsonify({
        'success': True,
        'message': '标签删除成功'
    })

@admin_app.route('/api/admin/dashboard', methods=['GET'])
@admin_login_required
def get_dashboard():
    total_users = User.count_for_admin()
    total_posts = Post.count_for_admin()
    active_posts = Post.count_for_admin(status=Post.STATUS_ACTIVE)
    hidden_posts = Post.count_for_admin(status=Post.STATUS_HIDDEN)
    total_recharge = User.get_total_recharge()
    
    recent_users = User.get_all_for_admin(limit=5)
    recent_posts = Post.get_all_for_admin(limit=5)
    
    level_stats = {}
    for level_key in Config.USER_LEVELS.keys():
        count = User.count_for_admin(level=level_key)
        level_stats[level_key] = {
            'count': count,
            'name': Config.USER_LEVELS[level_key]['name']
        }
    
    pending_reports = Report.count_for_admin(status=Report.STATUS_PENDING)
    active_announcements = Announcement.count_for_admin(status=Announcement.STATUS_ACTIVE)
    banned_users = User.count_for_admin()
    
    return jsonify({
        'success': True,
        'dashboard': {
            'total_users': total_users,
            'total_posts': total_posts,
            'active_posts': active_posts,
            'hidden_posts': hidden_posts,
            'total_recharge': total_recharge,
            'pending_reports': pending_reports,
            'active_announcements': active_announcements,
            'level_distribution': level_stats,
            'recent_users': [u.to_dict() for u in recent_users],
            'recent_posts': [p.to_dict(include_author=True) for p in recent_posts]
        }
    })

@admin_app.route('/api/admin/reports', methods=['GET'])
@admin_login_required
def get_reports_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    status = request.args.get('status', '').strip()
    status_filter = status if status else None
    
    reports = Report.get_for_admin(
        limit=per_page,
        offset=offset,
        status=status_filter
    )
    
    total = Report.count_for_admin(status=status_filter)
    
    reports_data = []
    for report in reports:
        report_dict = report.to_dict(
            include_reporter=True,
            include_handler=True,
            include_target=True
        )
        reports_data.append(report_dict)
    
    return jsonify({
        'success': True,
        'reports': reports_data,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })

@admin_app.route('/api/admin/reports/<int:report_id>', methods=['GET'])
@admin_login_required
def get_report_detail(report_id):
    report = Report.get_by_id(report_id)
    
    if not report:
        return jsonify({'success': False, 'message': '举报不存在'}), 404
    
    return jsonify({
        'success': True,
        'report': report.to_dict(
            include_reporter=True,
            include_handler=True,
            include_target=True
        )
    })

@admin_app.route('/api/admin/reports/<int:report_id>/resolve', methods=['POST'])
@admin_login_required
def resolve_report(report_id):
    admin = get_current_admin()
    report = Report.get_by_id(report_id)
    
    if not report:
        return jsonify({'success': False, 'message': '举报不存在'}), 404
    
    if not report.is_pending():
        return jsonify({'success': False, 'message': '该举报已被处理'}), 400
    
    data = request.get_json() or {}
    note = data.get('note', '').strip()
    
    report.resolve(admin.id, note=note if note else None)
    
    return jsonify({
        'success': True,
        'message': '举报已处理',
        'report': report.to_dict(include_reporter=True, include_handler=True)
    })

@admin_app.route('/api/admin/reports/<int:report_id>/dismiss', methods=['POST'])
@admin_login_required
def dismiss_report(report_id):
    admin = get_current_admin()
    report = Report.get_by_id(report_id)
    
    if not report:
        return jsonify({'success': False, 'message': '举报不存在'}), 404
    
    if not report.is_pending():
        return jsonify({'success': False, 'message': '该举报已被处理'}), 400
    
    data = request.get_json() or {}
    note = data.get('note', '').strip()
    
    report.dismiss(admin.id, note=note if note else None)
    
    return jsonify({
        'success': True,
        'message': '举报已驳回',
        'report': report.to_dict(include_reporter=True, include_handler=True)
    })

@admin_app.route('/api/admin/reports/stats', methods=['GET'])
@admin_login_required
def get_reports_stats():
    total_reports = Report.count_for_admin()
    pending_reports = Report.count_for_admin(status=Report.STATUS_PENDING)
    resolved_reports = Report.count_for_admin(status=Report.STATUS_RESOLVED)
    dismissed_reports = Report.count_for_admin(status=Report.STATUS_DISMISSED)
    
    return jsonify({
        'success': True,
        'stats': {
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'resolved_reports': resolved_reports,
            'dismissed_reports': dismissed_reports
        }
    })

@admin_app.route('/api/admin/users/<int:user_id>/ban', methods=['POST'])
@admin_login_required
def ban_user(user_id):
    admin = get_current_admin()
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if user.is_banned_user():
        return jsonify({'success': False, 'message': '该用户已被封禁'}), 400
    
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()
    
    user.ban(admin.id, reason=reason if reason else None)
    
    return jsonify({
        'success': True,
        'message': '用户已封禁',
        'user': user.to_dict(include_admin_info=True)
    })

@admin_app.route('/api/admin/users/<int:user_id>/unban', methods=['POST'])
@admin_login_required
def unban_user(user_id):
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if not user.is_banned_user():
        return jsonify({'success': False, 'message': '该用户未被封禁'}), 400
    
    user.unban()
    
    return jsonify({
        'success': True,
        'message': '用户已解封',
        'user': user.to_dict(include_admin_info=True)
    })

@admin_app.route('/api/admin/posts/<int:post_id>/pin', methods=['POST'])
@admin_login_required
def admin_pin_post(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404
    
    if post.is_pinned:
        return jsonify({'success': False, 'message': '该帖子已置顶'}), 400
    
    data = request.get_json() or {}
    duration_days = data.get('duration_days', 30)
    
    try:
        duration_days = int(duration_days)
        if duration_days <= 0:
            raise ValueError()
    except:
        return jsonify({'success': False, 'message': '无效的置顶天数'}), 400
    
    post.pin(duration_days=duration_days)
    
    return jsonify({
        'success': True,
        'message': f'帖子已置顶，有效期{duration_days}天',
        'post': post.to_dict(include_author=True, include_admin_info=True)
    })

@admin_app.route('/api/admin/posts/<int:post_id>/unpin', methods=['POST'])
@admin_login_required
def admin_unpin_post(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404
    
    if not post.is_pinned:
        return jsonify({'success': False, 'message': '该帖子未置顶'}), 400
    
    post.unpin()
    
    return jsonify({
        'success': True,
        'message': '帖子已取消置顶',
        'post': post.to_dict(include_author=True, include_admin_info=True)
    })

@admin_app.route('/api/admin/announcements', methods=['GET'])
@admin_login_required
def get_announcements_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    status = request.args.get('status', '').strip()
    status_filter = status if status else None
    
    announcements = Announcement.get_for_admin(
        limit=per_page,
        offset=offset,
        status=status_filter
    )
    
    total = Announcement.count_for_admin(status=status_filter)
    
    return jsonify({
        'success': True,
        'announcements': [a.to_dict(include_admin=True) for a in announcements],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })

@admin_app.route('/api/admin/announcements/<int:announcement_id>', methods=['GET'])
@admin_login_required
def get_announcement_admin_detail(announcement_id):
    announcement = Announcement.get_by_id(announcement_id)
    
    if not announcement:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    return jsonify({
        'success': True,
        'announcement': announcement.to_dict(include_admin=True)
    })

@admin_app.route('/api/admin/announcements', methods=['POST'])
@admin_login_required
def create_announcement():
    admin = get_current_admin()
    data = request.get_json()
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    is_pinned = data.get('is_pinned', 0)
    
    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400
    
    try:
        is_pinned = int(is_pinned)
    except:
        is_pinned = 0
    
    announcement = Announcement.create(
        admin_id=admin.id,
        title=title,
        content=content,
        is_pinned=is_pinned
    )
    
    return jsonify({
        'success': True,
        'message': '公告发布成功',
        'announcement': announcement.to_dict(include_admin=True)
    })

@admin_app.route('/api/admin/announcements/<int:announcement_id>', methods=['PUT'])
@admin_login_required
def update_announcement(announcement_id):
    announcement = Announcement.get_by_id(announcement_id)
    
    if not announcement:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    is_pinned = data.get('is_pinned')
    status = data.get('status')
    
    updates = {}
    if title is not None:
        updates['title'] = title.strip() if title else None
    if content is not None:
        updates['content'] = content.strip() if content else None
    if is_pinned is not None:
        try:
            updates['is_pinned'] = int(is_pinned)
        except:
            pass
    if status is not None:
        updates['status'] = status
    
    if not updates:
        return jsonify({'success': False, 'message': '没有需要更新的内容'}), 400
    
    announcement.update(**updates)
    
    return jsonify({
        'success': True,
        'message': '公告更新成功',
        'announcement': announcement.to_dict(include_admin=True)
    })

@admin_app.route('/api/admin/announcements/<int:announcement_id>/pin', methods=['POST'])
@admin_login_required
def pin_announcement(announcement_id):
    announcement = Announcement.get_by_id(announcement_id)
    
    if not announcement:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    if announcement.is_pinned:
        return jsonify({'success': False, 'message': '该公告已置顶'}), 400
    
    announcement.pin()
    
    return jsonify({
        'success': True,
        'message': '公告已置顶',
        'announcement': announcement.to_dict(include_admin=True)
    })

@admin_app.route('/api/admin/announcements/<int:announcement_id>/unpin', methods=['POST'])
@admin_login_required
def unpin_announcement(announcement_id):
    announcement = Announcement.get_by_id(announcement_id)
    
    if not announcement:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    if not announcement.is_pinned:
        return jsonify({'success': False, 'message': '该公告未置顶'}), 400
    
    announcement.unpin()
    
    return jsonify({
        'success': True,
        'message': '公告已取消置顶',
        'announcement': announcement.to_dict(include_admin=True)
    })

@admin_app.route('/api/admin/announcements/<int:announcement_id>', methods=['DELETE'])
@admin_login_required
def delete_announcement(announcement_id):
    announcement = Announcement.get_by_id(announcement_id)
    
    if not announcement:
        return jsonify({'success': False, 'message': '公告不存在'}), 404
    
    announcement.delete()
    
    return jsonify({
        'success': True,
        'message': '公告已删除'
    })

@admin_app.route('/api/admin/announcements/stats', methods=['GET'])
@admin_login_required
def get_announcements_stats():
    total_announcements = Announcement.count_for_admin()
    active_announcements = Announcement.count_for_admin(status=Announcement.STATUS_ACTIVE)
    inactive_announcements = Announcement.count_for_admin(status=Announcement.STATUS_INACTIVE)
    
    return jsonify({
        'success': True,
        'stats': {
            'total_announcements': total_announcements,
            'active_announcements': active_announcements,
            'inactive_announcements': inactive_announcements
        }
    })

@admin_app.route('/')
def admin_index():
    if os.path.exists(os.path.join(ADMIN_STATIC_FOLDER, 'index.html')):
        return send_from_directory(ADMIN_STATIC_FOLDER, 'index.html')
    return jsonify({
        'success': True,
        'message': '公告平台后台管理服务运行中',
        'info': '这是后台管理API服务，运行在端口 3009',
        'api_base': '/api/admin',
        'default_login': {
            'username': 'admin',
            'password': 'admin123'
        }
    })

@admin_app.route('/health')
def admin_health_check():
    return jsonify({
        'success': True,
        'message': '服务运行正常',
        'service': 'admin-backend',
        'port': 3009
    })

@admin_app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(ADMIN_STATIC_FOLDER, 'assets'), filename)

@admin_app.route('/<path:path>')
def serve_spa(path):
    if path.startswith('api/'):
        return jsonify({'success': False, 'message': '接口不存在'}), 404
    
    if os.path.exists(os.path.join(ADMIN_STATIC_FOLDER, path)):
        return send_from_directory(ADMIN_STATIC_FOLDER, path)
    
    if os.path.exists(os.path.join(ADMIN_STATIC_FOLDER, 'index.html')):
        return send_from_directory(ADMIN_STATIC_FOLDER, 'index.html')
    
    return jsonify({
        'success': False,
        'message': '页面不存在，后台管理前端尚未部署',
        'info': '请先构建后台管理前端并部署到 admin_static 目录'
    }), 404

@admin_app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': '接口不存在'}), 404

@admin_app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    admin_app.run(debug=True, host='0.0.0.0', port=3009, use_reloader=False)
