import os
import sys

os.environ['DATABASE_HOST'] = 'localhost'
os.environ['DATABASE_PORT'] = '5436'
os.environ['DATABASE_NAME'] = 'appdb'
os.environ['DATABASE_USER'] = 'appuser'
os.environ['DATABASE_PASSWORD'] = 'apppassword'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import execute, fetchone, fetchall

def test_execute_returning():
    print("测试 execute 函数的 RETURNING 功能...")
    
    try:
        test_username = f'test_user_{os.urandom(4).hex()}'
        test_password = 'test123'
        test_email = f'{test_username}@test.com'
        
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(test_password)
        
        user_id = execute(
            'INSERT INTO users (username, password, email) VALUES (%s, %s, %s) RETURNING id',
            (test_username, hashed_password, test_email)
        )
        
        print(f"  创建用户返回的 user_id: {user_id}")
        print(f"  user_id 类型: {type(user_id)}")
        
        assert user_id is not None, "execute 应该返回有效的 user_id"
        assert isinstance(user_id, int), f"user_id 应该是整数类型，但得到 {type(user_id)}"
        
        user = fetchone('SELECT * FROM users WHERE id = %s', (user_id,))
        assert user is not None, "应该能找到刚创建的用户"
        assert user['username'] == test_username, "用户名应该匹配"
        
        print(f"  验证用户数据: username={user['username']}, email={user['email']}")
        
        execute('DELETE FROM users WHERE id = %s', (user_id,))
        print("  清理测试数据完成")
        
        print("✅ execute 函数测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_model():
    print("\n测试 User 模型...")
    
    try:
        from models import User
        
        test_username = f'test_model_{os.urandom(4).hex()}'
        test_password = 'test123'
        test_email = f'{test_username}@test.com'
        
        user = User.create(test_username, test_password, test_email)
        
        print(f"  创建用户: id={user.id}, username={user.username}")
        
        assert user is not None, "User.create 应该返回 User 对象"
        assert user.id is not None, "用户应该有 id"
        assert user.username == test_username, "用户名应该匹配"
        assert user.email == test_email, "邮箱应该匹配"
        
        found_user = User.get_by_id(user.id)
        assert found_user is not None, "应该能通过 id 找到用户"
        assert found_user.username == test_username, "用户名应该匹配"
        
        found_by_username = User.get_by_username(test_username)
        assert found_by_username is not None, "应该能通过用户名找到用户"
        assert found_by_username.id == user.id, "用户 id 应该匹配"
        
        execute('DELETE FROM users WHERE id = %s', (user.id,))
        print("  清理测试数据完成")
        
        print("✅ User 模型测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_registration_flow():
    print("\n测试完整注册流程...")
    
    try:
        import json
        from werkzeug.test import Client
        from werkzeug.wrappers import Response
        
        os.environ['SECRET_KEY'] = 'test_secret_key_for_testing'
        
        from app import app
        
        client = Client(app, Response)
        
        test_username = f'test_reg_{os.urandom(4).hex()}'
        test_password = 'test123456'
        test_email = f'{test_username}@test.com'
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': test_username,
                'password': test_password,
                'confirm_password': test_password,
                'email': test_email
            }),
            content_type='application/json'
        )
        
        print(f"  响应状态码: {response.status}")
        print(f"  响应数据: {response.data.decode('utf-8')}")
        
        assert response.status_code == 200, f"应该返回 200，但得到 {response.status_code}"
        
        data = json.loads(response.data.decode('utf-8'))
        assert data.get('success') == True, f"注册应该成功，但响应是: {data}"
        assert 'user' in data, "响应应该包含用户信息"
        assert data['user']['username'] == test_username, "用户名应该匹配"
        
        print(f"  注册的用户: {data['user']}")
        
        user_id = data['user']['id']
        execute('DELETE FROM users WHERE id = %s', (user_id,))
        print("  清理测试数据完成")
        
        print("✅ 完整注册流程测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("开始测试注册功能修复...")
    print("=" * 60)
    
    results = []
    
    results.append(test_execute_returning())
    results.append(test_user_model())
    results.append(test_complete_registration_flow())
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    if all(results):
        print("✅ 所有测试通过！修复成功！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
