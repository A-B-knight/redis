#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

import os

# Redis 配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Flask 配置
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
SESSION_EXPIRE_TIME = 3600  # 会话过期时间（秒）

# 应用配置
TASKS_PER_PAGE = 10  # 每页显示的任务数

