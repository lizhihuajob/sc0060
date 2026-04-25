import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from config import Config

from init_db import init_database
init_database()

from models import User, Post, Transaction

app = Flask(__name__)
app.config.from_object(Config)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.get_by_id(session['user_id'])
    return None

@app.context_processor
def inject_user():
    user = get_current_user()
    return dict(current_user=user, Config=Config)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    current_user = get_current_user()
    posts = Post.get_visible_posts(current_user, limit=per_page, offset=offset)
    
    return render_template('index.html', posts=posts, page=page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        email = request.form.get('email', '').strip()
        
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('register'))
        
        if User.get_by_username(username):
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))
        
        user = User.create(username, password, email)
        session['user_id'] = user.id
        flash('注册成功！欢迎加入', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    transactions = Transaction.get_by_user(user.id, limit=10)
    return render_template('profile.html', transactions=transactions)

@app.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    user = get_current_user()
    
    if request.method == 'POST':
        target_level = request.form.get('level', '')
        
        if target_level not in Config.USER_LEVELS:
            flash('无效的等级', 'danger')
            return redirect(url_for('upgrade'))
        
        level_info = Config.USER_LEVELS[target_level]
        current_level_order = list(Config.USER_LEVELS.keys())
        current_index = current_level_order.index(user.level)
        target_index = current_level_order.index(target_level)
        
        if target_index <= current_index:
            flash('只能升级到更高等级', 'danger')
            return redirect(url_for('upgrade'))
        
        if user.balance < level_info['price']:
            flash(f'余额不足，需要 {level_info["price"]} 元', 'danger')
            return redirect(url_for('upgrade'))
        
        old_level_name = user.get_level_info()['name']
        if user.upgrade_level(target_level):
            Transaction.create(
                user.id,
                -level_info['price'],
                Transaction.TYPE_UPGRADE,
                f'从{old_level_name}升级到{level_info["name"]}'
            )
            flash(f'升级成功！您现在是{level_info["name"]}会员', 'success')
        else:
            flash('升级失败', 'danger')
        
        return redirect(url_for('upgrade'))
    
    return render_template('upgrade.html')

@app.route('/recharge', methods=['GET', 'POST'])
@login_required
def recharge():
    user = get_current_user()
    
    if request.method == 'POST':
        amount = request.form.get('amount', '0')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
        except:
            flash('请输入有效的充值金额', 'danger')
            return redirect(url_for('recharge'))
        
        user.add_balance(amount)
        Transaction.create(
            user.id,
            amount,
            Transaction.TYPE_RECHARGE,
            f'充值 {amount} 元'
        )
        flash(f'充值成功！已到账 {amount} 元', 'success')
        return redirect(url_for('recharge'))
    
    transactions = Transaction.get_by_user(user.id, limit=20)
    return render_template('recharge.html', transactions=transactions)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    user = get_current_user()
    
    if not user.can_post():
        flash(f'您的发布数量已达上限（{user.posts_count}/{user.get_posts_limit()}），请升级会员等级', 'warning')
        return redirect(url_for('upgrade'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        view_permission = request.form.get('view_permission', 'all')
        is_task = int(request.form.get('is_task', 0))
        
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('new_post'))
        
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
        
        if is_task:
            flash('任务发布成功！', 'success')
        else:
            flash('公告发布成功！', 'success')
        
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template('new_post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        flash('该公告不存在', 'danger')
        return redirect(url_for('index'))
    
    current_user = get_current_user()
    if not post.is_visible_to(current_user):
        flash('您没有权限查看该公告', 'danger')
        return redirect(url_for('index'))
    
    return render_template('post_detail.html', post=post)

@app.route('/my-posts')
@login_required
def my_posts():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    posts = Post.get_by_user(user.id, limit=per_page, offset=offset)
    
    return render_template('my_posts.html', posts=posts, page=page)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
