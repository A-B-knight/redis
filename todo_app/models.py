#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型和业务逻辑
"""

import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from redis_client import redis_client
from config import SESSION_EXPIRE_TIME


class User:
    """用户模型"""
    
    @staticmethod
    def create(username: str, password: str) -> Optional[Dict]:
        """创建用户"""
        user_key = f'user:{username}'
        
        # 检查用户是否已存在
        if redis_client.exists(user_key):
            return None
        
        # 创建用户数据
        user_data = {
            'username': username,
            'password': password,  # 实际应用中应该使用哈希
            'created_at': time.time(),
            'tasks_count': 0,
            'completed_count': 0
        }
        
        # 存储用户信息
        redis_client.hset(user_key, mapping=user_data)
        
        # 添加到用户集合
        redis_client.sadd('users', username)
        
        return user_data
    
    @staticmethod
    def get(username: str) -> Optional[Dict]:
        """获取用户信息"""
        user_key = f'user:{username}'
        if not redis_client.exists(user_key):
            return None
        
        return redis_client.hgetall(user_key)
    
    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """验证用户"""
        user = User.get(username)
        if not user:
            return False
        return user.get('password') == password
    
    @staticmethod
    def update_stats(username: str, tasks_delta: int = 0, completed_delta: int = 0):
        """更新用户统计"""
        user_key = f'user:{username}'
        pipe = redis_client.pipeline()
        
        if tasks_delta != 0:
            pipe.hincrby(user_key, 'tasks_count', tasks_delta)
        if completed_delta != 0:
            pipe.hincrby(user_key, 'completed_count', completed_delta)
        
        pipe.execute()


class Session:
    """会话管理"""
    
    @staticmethod
    def create(username: str) -> str:
        """创建会话"""
        session_id = str(uuid.uuid4())
        session_key = f'session:{session_id}'
        
        session_data = {
            'username': username,
            'created_at': time.time()
        }
        
        # 存储会话数据，设置过期时间
        redis_client.set(
            session_key,
            json.dumps(session_data),
            ex=SESSION_EXPIRE_TIME
        )
        
        # 记录用户的会话ID
        redis_client.sadd(f'user:{username}:sessions', session_id)
        
        return session_id
    
    @staticmethod
    def get(session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        session_key = f'session:{session_id}'
        session_data = redis_client.get(session_key)
        
        if not session_data:
            return None
        
        return json.loads(session_data)
    
    @staticmethod
    def delete(session_id: str):
        """删除会话"""
        session = Session.get(session_id)
        if session:
            username = session.get('username')
            session_key = f'session:{session_id}'
            redis_client.delete(session_key)
            redis_client.srem(f'user:{username}:sessions', session_id)
    
    @staticmethod
    def refresh(session_id: str):
        """刷新会话过期时间"""
        session_key = f'session:{session_id}'
        if redis_client.exists(session_key):
            redis_client.expire(session_key, SESSION_EXPIRE_TIME)


class Task:
    """任务模型"""
    
    @staticmethod
    def create(username: str, title: str, description: str = '') -> Dict:
        """创建任务"""
        task_id = str(uuid.uuid4())
        task_key = f'task:{task_id}'
        
        task_data = {
            'id': task_id,
            'username': username,
            'title': title,
            'description': description,
            'status': 'pending',  # pending, completed
            'created_at': str(time.time()),
            'updated_at': str(time.time()),
            'completed_at': ''  # 空字符串表示未完成
        }
        
        # 存储任务数据（过滤掉 None 值）
        task_data_clean = {k: (v if v is not None else '') for k, v in task_data.items()}
        redis_client.hset(task_key, mapping=task_data_clean)
        
        # 添加到用户的任务列表（按创建时间排序）
        timestamp = time.time()
        redis_client.zadd(f'user:{username}:tasks', {task_id: timestamp})
        
        # 添加到所有任务集合
        redis_client.sadd('all_tasks', task_id)
        
        # 更新用户统计
        User.update_stats(username, tasks_delta=1)
        
        # 发布任务创建通知
        redis_client.publish(
            f'user:{username}:notifications',
            json.dumps({
                'type': 'task_created',
                'task_id': task_id,
                'title': title,
                'timestamp': timestamp
            })
        )
        
        return task_data
    
    @staticmethod
    def get(task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        task_key = f'task:{task_id}'
        if not redis_client.exists(task_key):
            return None
        
        task_data = redis_client.hgetall(task_key)
        # 转换时间戳为浮点数
        if task_data.get('created_at'):
            task_data['created_at'] = float(task_data['created_at'])
        if task_data.get('updated_at'):
            task_data['updated_at'] = float(task_data['updated_at'])
        if task_data.get('completed_at'):
            # 空字符串表示未完成，转换为 None
            task_data['completed_at'] = float(task_data['completed_at']) if task_data['completed_at'] else None
        else:
            task_data['completed_at'] = None
        
        return task_data
    
    @staticmethod
    def update(task_id: str, title: str = None, description: str = None) -> Optional[Dict]:
        """更新任务"""
        task = Task.get(task_id)
        if not task:
            return None
        
        task_key = f'task:{task_id}'
        updates = {'updated_at': str(time.time())}
        
        if title is not None:
            updates['title'] = title
        if description is not None:
            updates['description'] = description
        
        redis_client.hset(task_key, mapping=updates)
        
        # 发布更新通知
        redis_client.publish(
            f'user:{task["username"]}:notifications',
            json.dumps({
                'type': 'task_updated',
                'task_id': task_id,
                'timestamp': time.time()
            })
        )
        
        return Task.get(task_id)
    
    @staticmethod
    def toggle_status(task_id: str) -> Optional[Dict]:
        """切换任务状态（完成/未完成）"""
        task = Task.get(task_id)
        if not task:
            return None
        
        task_key = f'task:{task_id}'
        username = task['username']
        current_status = task['status']
        new_status = 'completed' if current_status == 'pending' else 'pending'
        
        updates = {
            'status': new_status,
            'updated_at': str(time.time())
        }
        
        if new_status == 'completed':
            updates['completed_at'] = str(time.time())
            User.update_stats(username, completed_delta=1)
            # 更新排行榜
            Leaderboard.update(username, 1)
        else:
            updates['completed_at'] = ''  # 空字符串表示未完成
            User.update_stats(username, completed_delta=-1)
            # 更新排行榜
            Leaderboard.update(username, -1)
        
        redis_client.hset(task_key, mapping=updates)
        
        # 发布状态变更通知
        redis_client.publish(
            f'user:{username}:notifications',
            json.dumps({
                'type': 'task_status_changed',
                'task_id': task_id,
                'status': new_status,
                'timestamp': time.time()
            })
        )
        
        return Task.get(task_id)
    
    @staticmethod
    def delete(task_id: str) -> bool:
        """删除任务"""
        task = Task.get(task_id)
        if not task:
            return False
        
        username = task['username']
        task_key = f'task:{task_id}'
        
        # 删除任务数据
        redis_client.delete(task_key)
        
        # 从用户任务列表中移除
        redis_client.zrem(f'user:{username}:tasks', task_id)
        
        # 从所有任务集合中移除
        redis_client.srem('all_tasks', task_id)
        
        # 更新用户统计
        if task['status'] == 'completed':
            User.update_stats(username, tasks_delta=-1, completed_delta=-1)
        else:
            User.update_stats(username, tasks_delta=-1)
        
        # 发布删除通知
        redis_client.publish(
            f'user:{username}:notifications',
            json.dumps({
                'type': 'task_deleted',
                'task_id': task_id,
                'timestamp': time.time()
            })
        )
        
        return True
    
    @staticmethod
    def list_by_user(username: str, status: str = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取用户的任务列表"""
        tasks_key = f'user:{username}:tasks'
        
        # 获取任务ID列表（按创建时间降序）
        task_ids = redis_client.zrevrange(tasks_key, offset, offset + limit - 1)
        
        tasks = []
        for task_id in task_ids:
            task = Task.get(task_id)
            if task:
                # 如果指定了状态过滤
                if status is None or task['status'] == status:
                    tasks.append(task)
        
        return tasks
    
    @staticmethod
    def count_by_user(username: str, status: str = None) -> int:
        """统计用户的任务数量"""
        tasks = Task.list_by_user(username, status=status, limit=10000)
        return len(tasks)


class Leaderboard:
    """排行榜（任务完成统计）"""
    
    @staticmethod
    def update(username: str, score_delta: int = 1):
        """更新排行榜分数"""
        redis_client.zincrby('leaderboard:completed_tasks', score_delta, username)
    
    @staticmethod
    def get_top(n: int = 10) -> List[tuple]:
        """获取前N名"""
        return redis_client.zrevrange('leaderboard:completed_tasks', 0, n - 1, withscores=True)
    
    @staticmethod
    def get_rank(username: str) -> Optional[int]:
        """获取用户排名（从1开始）"""
        rank = redis_client.zrevrank('leaderboard:completed_tasks', username)
        return rank + 1 if rank is not None else None
    
    @staticmethod
    def get_score(username: str) -> float:
        """获取用户分数"""
        score = redis_client.zscore('leaderboard:completed_tasks', username)
        return score if score else 0.0

