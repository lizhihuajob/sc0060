import os
import sys

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
wal_path = db_path + '-wal'
shm_path = db_path + '-shm'

for path in [db_path, wal_path, shm_path]:
    if os.path.exists(path):
        os.remove(path)
        print(f'Removed: {path}')

from init_db import init_database
init_database()
print('Database initialized successfully!')

from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
