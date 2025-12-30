#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis 学习示例代码
演示 Redis 的各种数据类型和常见使用场景
"""

import redis
import json
import time
from typing import Optional, Dict, Any


# 连接到 Redis
# decode_responses=True 表示自动将字节解码为字符串
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def test_connection():
    """测试 Redis 连接"""
    print("=" * 50)
    print("1. 测试连接")
    print("=" * 50)
    try:
        result = r.ping()
        print(f"✓ 连接成功: {result}")
        print(f"✓ Redis 版本: {r.info()['redis_version']}")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print("请确保 Redis 服务器正在运行！")
        return False
    return True


def example_strings():
    """字符串操作示例"""
    print("\n" + "=" * 50)
    print("2. 字符串 (String) 操作")
    print("=" * 50)
    
    # 基本设置和获取
    r.set('name', 'Redis学习')
    print(f"设置 name: {r.get('name')}")
    
    # 计数器
    r.set('counter', 0)
    r.incr('counter')
    r.incr('counter', 5)  # 增加5
    print(f"计数器值: {r.get('counter')}")
    
    # 设置过期时间
    r.setex('temp_key', 10, '10秒后过期')
    ttl = r.ttl('temp_key')
    print(f"临时键剩余时间: {ttl} 秒")
    
    # 批量操作
    r.mset({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'})
    values = r.mget('key1', 'key2', 'key3')
    print(f"批量获取: {values}")


def example_hashes():
    """哈希操作示例"""
    print("\n" + "=" * 50)
    print("3. 哈希 (Hash) 操作 - 存储用户信息")
    print("=" * 50)
    
    # 存储用户信息
    user_id = 1001
    user_key = f'user:{user_id}'
    r.hset(user_key, mapping={
        'name': '张三',
        'age': 25,
        'email': 'zhangsan@example.com',
        'city': '北京'
    })
    
    # 获取所有字段
    user_info = r.hgetall(user_key)
    print(f"用户信息: {user_info}")
    
    # 获取单个字段
    name = r.hget(user_key, 'name')
    print(f"用户名: {name}")
    
    # 更新单个字段
    r.hset(user_key, 'age', 26)
    print(f"更新后的年龄: {r.hget(user_key, 'age')}")
    
    # 检查字段是否存在
    exists = r.hexists(user_key, 'email')
    print(f"email 字段存在: {exists}")


def example_lists():
    """列表操作示例"""
    print("\n" + "=" * 50)
    print("4. 列表 (List) 操作 - 消息队列")
    print("=" * 50)
    
    queue_name = 'message_queue'
    
    # 从左侧推入（作为队列使用）
    r.lpush(queue_name, '消息1', '消息2', '消息3')
    
    # 查看所有消息
    messages = r.lrange(queue_name, 0, -1)
    print(f"所有消息: {messages}")
    
    # 从右侧弹出（FIFO 队列）
    message = r.rpop(queue_name)
    print(f"处理消息: {message}")
    
    # 查看剩余消息
    remaining = r.lrange(queue_name, 0, -1)
    print(f"剩余消息: {remaining}")
    
    # 获取列表长度
    length = r.llen(queue_name)
    print(f"队列长度: {length}")


def example_sets():
    """集合操作示例"""
    print("\n" + "=" * 50)
    print("5. 集合 (Set) 操作 - 标签系统")
    print("=" * 50)
    
    # 文章1的标签
    r.sadd('article:1:tags', 'Python', 'Redis', '数据库', '缓存')
    
    # 文章2的标签
    r.sadd('article:2:tags', 'Python', 'Web开发', 'Django')
    
    # 文章3的标签
    r.sadd('article:3:tags', 'Redis', '数据库', 'NoSQL')
    
    # 获取文章1的所有标签
    tags1 = r.smembers('article:1:tags')
    print(f"文章1的标签: {tags1}")
    
    # 查找共同标签（交集）
    common_tags = r.sinter('article:1:tags', 'article:2:tags')
    print(f"文章1和文章2的共同标签: {common_tags}")
    
    # 所有标签（并集）
    all_tags = r.sunion('article:1:tags', 'article:2:tags', 'article:3:tags')
    print(f"所有文章的标签: {all_tags}")
    
    # 检查标签是否存在
    has_python = r.sismember('article:1:tags', 'Python')
    print(f"文章1是否有Python标签: {has_python}")


def example_sorted_sets():
    """有序集合操作示例 - 排行榜"""
    print("\n" + "=" * 50)
    print("6. 有序集合 (Sorted Set) 操作 - 游戏排行榜")
    print("=" * 50)
    
    leaderboard = 'game:leaderboard'
    
    # 添加玩家分数
    r.zadd(leaderboard, {
        'player1': 1000,
        'player2': 2500,
        'player3': 1800,
        'player4': 3200,
        'player5': 1500
    })
    
    # 更新玩家分数
    r.zincrby(leaderboard, 500, 'player1')
    print(f"player1 新分数: {r.zscore(leaderboard, 'player1')}")
    
    # 获取前3名（降序）
    top_3 = r.zrevrange(leaderboard, 0, 2, withscores=True)
    print("前3名玩家:")
    for rank, (player, score) in enumerate(top_3, 1):
        print(f"  {rank}. {player}: {score} 分")
    
    # 获取玩家排名（从0开始，所以+1）
    rank = r.zrevrank(leaderboard, 'player1')
    print(f"player1 的排名: 第 {rank + 1} 名")
    
    # 获取分数范围内的玩家
    players_1500_2000 = r.zrangebyscore(leaderboard, 1500, 2000, withscores=True)
    print(f"分数在1500-2000之间的玩家: {players_1500_2000}")


def example_expiration():
    """过期时间示例"""
    print("\n" + "=" * 50)
    print("7. 过期时间 (TTL) 示例 - 会话管理")
    print("=" * 50)
    
    session_id = 'abc123xyz'
    session_key = f'session:{session_id}'
    
    # 设置会话，30分钟后过期
    session_data = {
        'user_id': 1001,
        'username': 'zhangsan',
        'login_time': time.time()
    }
    r.setex(session_key, 1800, json.dumps(session_data))  # 1800秒 = 30分钟
    
    # 查看剩余时间
    ttl = r.ttl(session_key)
    print(f"会话剩余时间: {ttl} 秒 ({ttl // 60} 分钟)")
    
    # 获取会话数据
    session = json.loads(r.get(session_key))
    print(f"会话数据: {session}")
    
    # 刷新过期时间
    r.expire(session_key, 3600)  # 延长到1小时
    print(f"刷新后的剩余时间: {r.ttl(session_key)} 秒")


def example_pipeline():
    """管道操作示例 - 批量操作"""
    print("\n" + "=" * 50)
    print("8. 管道 (Pipeline) 操作 - 批量执行")
    print("=" * 50)
    
    # 使用管道可以一次性执行多个命令，减少网络往返
    pipe = r.pipeline()
    
    pipe.set('pipe_key1', 'value1')
    pipe.set('pipe_key2', 'value2')
    pipe.incr('pipe_counter')
    pipe.incr('pipe_counter')
    pipe.get('pipe_key1')
    
    # 执行所有命令
    results = pipe.execute()
    print(f"管道执行结果: {results}")
    print(f"pipe_counter 的值: {r.get('pipe_counter')}")


def example_transactions():
    """事务操作示例"""
    print("\n" + "=" * 50)
    print("9. 事务 (Transaction) 操作")
    print("=" * 50)
    
    # 使用 MULTI/EXEC 执行事务
    pipe = r.pipeline()
    pipe.multi()
    pipe.set('tx_key1', 'value1')
    pipe.set('tx_key2', 'value2')
    pipe.incr('tx_counter')
    pipe.execute()
    
    print("事务执行完成")
    print(f"tx_key1: {r.get('tx_key1')}")
    print(f"tx_key2: {r.get('tx_key2')}")
    print(f"tx_counter: {r.get('tx_counter')}")


def example_pubsub():
    """发布订阅示例"""
    print("\n" + "=" * 50)
    print("10. 发布订阅 (Pub/Sub) 示例")
    print("=" * 50)
    print("注意: 发布订阅需要两个终端窗口来演示")
    print("在另一个终端运行: ./src/redis-cli")
    print("然后执行: SUBSCRIBE news")
    print("\n现在发布一条消息...")
    
    # 发布消息
    r.publish('news', '这是一条新闻消息')
    print("消息已发布到 'news' 频道")


def cleanup():
    """清理测试数据"""
    print("\n" + "=" * 50)
    print("清理测试数据")
    print("=" * 50)
    
    keys_to_delete = [
        'name', 'counter', 'temp_key', 'key1', 'key2', 'key3',
        'user:1001', 'message_queue', 'article:1:tags', 'article:2:tags', 
        'article:3:tags', 'game:leaderboard', 'session:abc123xyz',
        'pipe_key1', 'pipe_key2', 'pipe_counter', 'tx_key1', 'tx_key2', 'tx_counter'
    ]
    
    for key in keys_to_delete:
        r.delete(key)
    
    print("✓ 测试数据已清理")


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("Redis 学习示例")
    print("=" * 50)
    
    # 测试连接
    if not test_connection():
        return
    
    try:
        # 运行各种示例
        example_strings()
        example_hashes()
        example_lists()
        example_sets()
        example_sorted_sets()
        example_expiration()
        example_pipeline()
        example_transactions()
        example_pubsub()
        
        # 询问是否清理
        print("\n" + "=" * 50)
        response = input("是否清理测试数据? (y/n): ").strip().lower()
        if response == 'y':
            cleanup()
        
        print("\n" + "=" * 50)
        print("示例运行完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

