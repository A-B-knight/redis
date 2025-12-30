#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web 应用主文件
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import User, Session, Task, Leaderboard
from redis_client import redis_client
from config import SESSION_EXPIRE_TIME
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

# 注册时间格式化过滤器
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """将时间戳转换为可读日期"""
    try:
        return datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return 'N/A'

# 将 enumerate 添加到模板全局变量
@app.template_global()
def enumerate(iterable, start=0):
    """Jinja2 模板中的 enumerate 函数"""
    return __builtins__['enumerate'](iterable, start)


def get_current_user():
    """获取当前登录用户"""
    session_id = session.get('session_id')
    if not session_id:
        return None
    
    session_data = Session.get(session_id)
    if not session_data:
        return None
    
    # 刷新会话
    Session.refresh(session_id)
    
    return session_data.get('username')


@app.route('/')
def index():
    """首页"""
    username = get_current_user()
    if username:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('register.html', error='用户名和密码不能为空')
        
        user = User.create(username, password)
        if user:
            # 注册成功后自动登录
            session_id = Session.create(username)
            session['session_id'] = session_id
            return redirect(url_for('dashboard'))
        else:
            return render_template('register.html', error='用户名已存在')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='用户名和密码不能为空')
        
        if User.authenticate(username, password):
            # 创建会话
            session_id = Session.create(username)
            session['session_id'] = session_id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """用户登出"""
    session_id = session.get('session_id')
    if session_id:
        Session.delete(session_id)
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """任务管理面板"""
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))
    
    # 获取任务统计
    total_tasks = Task.count_by_user(username)
    completed_tasks = Task.count_by_user(username, status='completed')
    pending_tasks = Task.count_by_user(username, status='pending')
    
    # 获取用户信息
    user = User.get(username)
    
    # 获取排行榜信息
    user_rank = Leaderboard.get_rank(username)
    user_score = Leaderboard.get_score(username)
    top_users = Leaderboard.get_top(10)
    
    return render_template(
        'dashboard.html',
        username=username,
        user=user,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        user_rank=user_rank,
        user_score=int(user_score),
        top_users=top_users
    )


@app.route('/tasks')
def tasks():
    """任务列表页面"""
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status', 'all')  # all, pending, completed
    status = None if status_filter == 'all' else status_filter
    
    # 获取任务列表
    task_list = Task.list_by_user(username, status=status, limit=100)
    
    return render_template(
        'tasks.html',
        username=username,
        tasks=task_list,
        status_filter=status_filter
    )


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """创建任务 API"""
    username = get_current_user()
    if not username:
        return jsonify({'error': '未登录'}), 401
    
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    
    if not title:
        return jsonify({'error': '任务标题不能为空'}), 400
    
    task = Task.create(username, title, description)
    return jsonify({'success': True, 'task': task}), 201


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务 API"""
    username = get_current_user()
    if not username:
        return jsonify({'error': '未登录'}), 401
    
    task = Task.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    if task['username'] != username:
        return jsonify({'error': '无权访问'}), 403
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    
    task = Task.update(task_id, title=title, description=description)
    return jsonify({'success': True, 'task': task})


@app.route('/api/tasks/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """切换任务状态 API"""
    username = get_current_user()
    if not username:
        return jsonify({'error': '未登录'}), 401
    
    task = Task.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    if task['username'] != username:
        return jsonify({'error': '无权访问'}), 403
    
    task = Task.toggle_status(task_id)
    return jsonify({'success': True, 'task': task})


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务 API"""
    username = get_current_user()
    if not username:
        return jsonify({'error': '未登录'}), 401
    
    task = Task.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    if task['username'] != username:
        return jsonify({'error': '无权访问'}), 403
    
    Task.delete(task_id)
    return jsonify({'success': True})


@app.route('/api/stats')
def get_stats():
    """获取统计信息 API"""
    username = get_current_user()
    if not username:
        return jsonify({'error': '未登录'}), 401
    
    total_tasks = Task.count_by_user(username)
    completed_tasks = Task.count_by_user(username, status='completed')
    pending_tasks = Task.count_by_user(username, status='pending')
    
    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks
    })


if __name__ == '__main__':
    # 测试 Redis 连接
    try:
        if redis_client.ping():
            print("✓ Redis 连接成功")
        else:
            print("✗ Redis 连接失败")
            exit(1)
    except Exception as e:
        print(f"✗ Redis 连接错误: {e}")
        print("请确保 Redis 服务器正在运行！")
        exit(1)
    
    print("启动 Flask 应用...")
    print("访问 http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

