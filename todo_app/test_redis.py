#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 Redis 连接和基本功能
"""

from redis_client import redis_client
from models import User, Task, Leaderboard

def test_redis_connection():
    """测试 Redis 连接"""
    print("=" * 50)
    print("测试 Redis 连接")
    print("=" * 50)
    try:
        if redis_client.ping():
            print("✓ Redis 连接成功")
            info = redis_client.client.info()
            print(f"✓ Redis 版本: {info['redis_version']}")
            return True
        else:
            print("✗ Redis 连接失败")
            return False
    except Exception as e:
        print(f"✗ Redis 连接错误: {e}")
        print("\n请确保 Redis 服务器正在运行：")
        print("  cd /home/knight/code/redis")
        print("  ./src/redis-server")
        return False

def test_basic_operations():
    """测试基本操作"""
    print("\n" + "=" * 50)
    print("测试基本操作")
    print("=" * 50)
    
    # 测试用户创建
    print("\n1. 创建测试用户...")
    test_user = User.create('test_user', 'test_password')
    if test_user:
        print("✓ 用户创建成功")
    else:
        print("✗ 用户已存在或创建失败")
    
    # 测试任务创建
    print("\n2. 创建测试任务...")
    task = Task.create('test_user', '测试任务', '这是一个测试任务')
    if task:
        print(f"✓ 任务创建成功: {task['id']}")
    else:
        print("✗ 任务创建失败")
        return
    
    # 测试任务完成
    print("\n3. 完成任务...")
    completed_task = Task.toggle_status(task['id'])
    if completed_task and completed_task['status'] == 'completed':
        print("✓ 任务完成成功")
    else:
        print("✗ 任务完成失败")
    
    # 测试排行榜
    print("\n4. 查看排行榜...")
    top_users = Leaderboard.get_top(5)
    print("前5名用户:")
    for rank, (user, score) in enumerate(top_users, 1):
        print(f"  {rank}. {user}: {score} 分")
    
    # 清理测试数据
    print("\n5. 清理测试数据...")
    Task.delete(task['id'])
    print("✓ 测试完成")

if __name__ == '__main__':
    if test_redis_connection():
        test_basic_operations()
    else:
        print("\n请先启动 Redis 服务器！")

