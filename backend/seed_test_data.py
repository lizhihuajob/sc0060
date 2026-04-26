import os
import sys

os.environ['DATABASE_HOST'] = 'localhost'
os.environ['DATABASE_PORT'] = '5436'
os.environ['DATABASE_NAME'] = 'appdb'
os.environ['DATABASE_USER'] = 'appuser'
os.environ['DATABASE_PASSWORD'] = 'apppassword'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import User, Post, Transaction

print("=== 创建测试用户 ===")

test_users = [
    {'username': 'demo_bronze', 'password': 'demo123', 'email': 'bronze@demo.com', 'level': 'bronze'},
    {'username': 'demo_silver', 'password': 'demo123', 'email': 'silver@demo.com', 'level': 'silver'},
    {'username': 'demo_gold', 'password': 'demo123', 'email': 'gold@demo.com', 'level': 'gold'},
]

created_users = []
for user_data in test_users:
    existing = User.get_by_username(user_data['username'])
    if existing:
        print(f"用户 {user_data['username']} 已存在，跳过")
        created_users.append(existing)
    else:
        user = User.create(user_data['username'], user_data['password'], user_data['email'])
        if user_data['level'] != 'bronze':
            from database import execute
            execute('UPDATE users SET level = %s WHERE id = %s', (user_data['level'], user.id))
            user.level = user_data['level']
        print(f"创建用户: {user.username} (等级: {user_data['level']})")
        created_users.append(user)

print("\n=== 创建测试公告 ===")

test_posts = [
    {
        'title': '欢迎来到信息发布平台',
        'content': '这是一个功能完整的信息发布平台，您可以发布公告和任务。支持会员等级系统，不同等级有不同的发布数量限制和可见权限。欢迎体验！',
        'view_permission': 'all',
        'is_task': 0
    },
    {
        'title': '会员等级介绍',
        'content': '平台会员分为5个等级：\n\n青铜(免费)：可发布2条\n白银(10元)：可发布4条\n黄金(30元)：可发布8条\n黑金(100元)：可发布16条\n钻石(300元)：可发布32条\n\n每个等级是上一等级的2倍！',
        'view_permission': 'all',
        'is_task': 0
    },
    {
        'title': '【任务】招募测试人员',
        'content': '需要5名测试人员测试新功能。\n\n要求：\n1. 熟悉平台操作\n2. 有测试经验优先\n3. 能提供详细反馈\n\n有意者请联系管理员。',
        'view_permission': 'registered',
        'is_task': 1
    },
    {
        'title': '白银会员专属活动',
        'content': '为回馈白银及以上会员，我们特别推出以下活动：\n\n1. 本月内升级黄金会员享8折优惠\n2. 发布信息优先展示\n3. 专属客服支持\n\n详情请咨询客服。',
        'view_permission': 'silver_above',
        'is_task': 0
    },
    {
        'title': '【重要】黄金会员专属公告',
        'content': '尊敬的黄金及以上会员：\n\n感谢您的大力支持！为了提供更好的服务，我们将于本周六进行系统升级。\n\n升级时间：周六凌晨2:00-4:00\n影响范围：发布功能可能短暂不可用\n\n给您带来的不便，敬请谅解。',
        'view_permission': 'gold_above',
        'is_task': 0
    },
]

from database import fetchone, execute

for i, post_data in enumerate(test_posts):
    user_idx = i % len(created_users)
    user = created_users[user_idx]
    
    existing = fetchone('SELECT * FROM posts WHERE title = %s', (post_data['title'],))
    if existing:
        print(f"公告 \"{post_data['title'][:30]}...\" 已存在，跳过")
    else:
        post = Post.create(
            user_id=user.id,
            title=post_data['title'],
            content=post_data['content'],
            view_permission=post_data['view_permission'],
            is_task=post_data['is_task']
        )
        print(f"创建公告: {post.title[:30]}... (作者: {user.username}, 权限: {post_data['view_permission']})")

print("\n=== 测试数据创建完成 ===")
print("\n测试账号:")
print("  demo_bronze / demo123 (青铜)")
print("  demo_silver / demo123 (白银)")
print("  demo_gold / demo123 (黄金)")
