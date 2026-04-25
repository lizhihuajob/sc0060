import sqlite3
import os
import sys

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_database.db')
print(f'Database path: {db_path}')

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f'Removed existing database: {db_path}')
    except Exception as e:
        print(f'Error removing database: {e}')

print(f'Database exists before connect: {os.path.exists(db_path)}')

try:
    print('Connecting to database...')
    conn = sqlite3.connect(db_path)
    print(f'Database exists after connect: {os.path.exists(db_path)}')
    
    cursor = conn.cursor()
    print('Creating test table...')
    cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
    print('Table created successfully!')
    
    cursor.execute('INSERT INTO test (name) VALUES (?)', ('test',))
    print('Data inserted successfully!')
    
    conn.commit()
    cursor.close()
    conn.close()
    print('All operations completed successfully!')
    
    conn2 = sqlite3.connect(db_path)
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT * FROM test')
    result = cursor2.fetchall()
    print(f'Data read back: {result}')
    cursor2.close()
    conn2.close()
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f'Test database cleaned up.')
        
    print('SUCCESS: All tests passed!')
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
