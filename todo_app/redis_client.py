#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis 客户端封装
"""

import redis
import json
from config import REDIS_HOST, REDIS_PORT, REDIS_DB


class RedisClient:
    """Redis 客户端封装类"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
    
    def ping(self):
        """测试连接"""
        return self.client.ping()
    
    def get(self, key):
        """获取值"""
        return self.client.get(key)
    
    def set(self, key, value, ex=None):
        """设置值"""
        return self.client.set(key, value, ex=ex)
    
    def delete(self, *keys):
        """删除键"""
        return self.client.delete(*keys)
    
    def exists(self, key):
        """检查键是否存在"""
        return self.client.exists(key)
    
    def expire(self, key, time):
        """设置过期时间"""
        return self.client.expire(key, time)
    
    def ttl(self, key):
        """获取剩余过期时间"""
        return self.client.ttl(key)
    
    # 哈希操作
    def hset(self, key, mapping=None, **kwargs):
        """设置哈希字段"""
        if mapping:
            return self.client.hset(key, mapping=mapping)
        return self.client.hset(key, **kwargs)
    
    def hget(self, key, field):
        """获取哈希字段"""
        return self.client.hget(key, field)
    
    def hgetall(self, key):
        """获取所有哈希字段"""
        return self.client.hgetall(key)
    
    def hdel(self, key, *fields):
        """删除哈希字段"""
        return self.client.hdel(key, *fields)
    
    # 列表操作
    def lpush(self, key, *values):
        """从左侧推入"""
        return self.client.lpush(key, *values)
    
    def rpush(self, key, *values):
        """从右侧推入"""
        return self.client.rpush(key, *values)
    
    def lrange(self, key, start, end):
        """获取列表范围"""
        return self.client.lrange(key, start, end)
    
    def llen(self, key):
        """获取列表长度"""
        return self.client.llen(key)
    
    def lrem(self, key, count, value):
        """删除列表元素"""
        return self.client.lrem(key, count, value)
    
    # 集合操作
    def sadd(self, key, *values):
        """添加集合元素"""
        return self.client.sadd(key, *values)
    
    def smembers(self, key):
        """获取集合所有成员"""
        return self.client.smembers(key)
    
    def sismember(self, key, value):
        """检查是否是集合成员"""
        return self.client.sismember(key, value)
    
    def srem(self, key, *values):
        """删除集合元素"""
        return self.client.srem(key, *values)
    
    # 有序集合操作
    def zadd(self, key, mapping=None, **kwargs):
        """添加有序集合元素"""
        if mapping:
            return self.client.zadd(key, mapping=mapping)
        return self.client.zadd(key, **kwargs)
    
    def zincrby(self, key, amount, value):
        """增加有序集合分数"""
        return self.client.zincrby(key, amount, value)
    
    def zrevrange(self, key, start, end, withscores=False):
        """获取有序集合范围（降序）"""
        return self.client.zrevrange(key, start, end, withscores=withscores)
    
    def zscore(self, key, value):
        """获取有序集合分数"""
        return self.client.zscore(key, value)
    
    def zrevrank(self, key, value):
        """获取有序集合排名（降序）"""
        return self.client.zrevrank(key, value)
    
    def zrem(self, key, *values):
        """删除有序集合元素"""
        return self.client.zrem(key, *values)
    
    # 发布订阅
    def publish(self, channel, message):
        """发布消息"""
        return self.client.publish(channel, message)
    
    # 管道操作
    def pipeline(self):
        """创建管道"""
        return self.client.pipeline()


# 全局 Redis 客户端实例
redis_client = RedisClient()

