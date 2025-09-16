#!/usr/bin/env python3
import sqlite3
import json
import cgi
import os
from datetime import datetime

# 数据库文件路径 - 使用绝对路径确保可靠性
DB_PATH = '/usr/share/nginx/html/data/homework.db'

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def get_homework_list():
    """获取作业列表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM homework_list ORDER BY created_at DESC")
    homework_list = cursor.fetchall()
    conn.close()
    
    # 转换为字典列表
    result = []
    for item in homework_list:
        result.append({
            'id': item[0],
            'content': item[1],
            'created_at': item[2]
        })
    return result

def add_homework(content):
    """添加新作业"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO homework_list (content) VALUES (?)", (content,))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def delete_homework(homework_id):
    """删除作业"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM homework_list WHERE id = ?", (homework_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0

# 主处理逻辑
print("Content-type: application/json\n")

try:
    # 获取请求方法
    method = os.environ.get('REQUEST_METHOD', 'GET')
    
    if method == 'GET':
        # 获取作业列表
        homework = get_homework_list()
        print(json.dumps({'status': 'success', 'data': homework}))
        
    elif method == 'POST':
        # 添加新作业
        form = cgi.FieldStorage()
        content = form.getvalue('content')
        if content:
            new_id = add_homework(content)
            print(json.dumps({'status': 'success', 'id': new_id}))
        else:
            print(json.dumps({'status': 'error', 'message': '内容不能为空'}))
            
    elif method == 'DELETE':
        # 删除作业
        form = cgi.FieldStorage()
        homework_id = form.getvalue('id')
        if homework_id and homework_id.isdigit():
            success = delete_homework(int(homework_id))
            if success:
                print(json.dumps({'status': 'success'}))
            else:
                print(json.dumps({'status': 'error', 'message': '删除失败，作业不存在'}))
        else:
            print(json.dumps({'status': 'error', 'message': '无效的作业ID'}))
            
    else:
        print(json.dumps({'status': 'error', 'message': '不支持的请求方法'}))

except Exception as e:
    print(json.dumps({'status': 'error', 'message': str(e)}))