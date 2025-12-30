# Redis 任务管理系统

这是一个基于 Redis 和 Flask 的完整任务管理系统，展示了 Redis 在实际项目中的应用。

## 项目特性

- ✅ **用户认证系统** - 使用 Redis 存储用户信息和会话
- ✅ **任务管理** - 创建、编辑、删除、完成任务
- ✅ **实时统计** - 任务完成统计和排行榜
- ✅ **会话管理** - 自动过期的用户会话
- ✅ **数据持久化** - 所有数据存储在 Redis 中

## Redis 功能展示

本项目展示了 Redis 的以下功能：

1. **字符串 (String)**
   - 存储会话数据
   - 设置过期时间

2. **哈希 (Hash)**
   - 存储用户信息
   - 存储任务详情

3. **有序集合 (Sorted Set)**
   - 任务列表（按创建时间排序）
   - 排行榜（按完成数排序）

4. **集合 (Set)**
   - 用户集合
   - 所有任务ID集合
   - 用户会话集合

5. **发布订阅 (Pub/Sub)**
   - 任务变更通知（预留功能）

## 安装和运行

### 前置条件

1. **Redis 服务器**
   ```bash
   # 如果还没有编译 Redis，先编译
   cd /home/knight/code/redis
   make
   
   # 启动 Redis 服务器（在一个终端窗口）
   ./src/redis-server
   ```

2. **Python 3.7+**

### 安装依赖

```bash
cd /home/knight/code/redis/todo_app
pip install -r requirements.txt
```

### 运行应用

```bash
python3 app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用指南

### 1. 注册账号

访问 `http://localhost:5000/register` 创建新账号。

### 2. 登录

使用注册的用户名和密码登录。

### 3. 创建任务

- 在任务列表页面点击"添加任务"
- 输入任务标题和描述
- 点击"保存"

### 4. 管理任务

- **完成/取消任务**: 点击任务前的复选框
- **编辑任务**: 点击"编辑"按钮
- **删除任务**: 点击"删除"按钮

### 5. 查看统计

在控制面板可以查看：
- 总任务数
- 已完成任务数
- 待完成任务数
- 排行榜排名

## 项目结构

```
todo_app/
├── app.py              # Flask 应用主文件
├── config.py           # 配置文件
├── models.py           # 数据模型和业务逻辑
├── redis_client.py     # Redis 客户端封装
├── requirements.txt    # Python 依赖
├── README.md          # 项目说明
└── templates/         # HTML 模板
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── tasks.html
```

## Redis 数据结构说明

### 用户数据
- `user:{username}` - 哈希，存储用户信息
- `users` - 集合，所有用户名

### 会话数据
- `session:{session_id}` - 字符串，会话数据（带过期时间）
- `user:{username}:sessions` - 集合，用户的所有会话ID

### 任务数据
- `task:{task_id}` - 哈希，任务详情
- `user:{username}:tasks` - 有序集合，用户的任务列表（按时间排序）
- `all_tasks` - 集合，所有任务ID

### 排行榜
- `leaderboard:completed_tasks` - 有序集合，按完成数排序的用户

### 通知（预留）
- `user:{username}:notifications` - 发布订阅频道

## 学习要点

### 1. 会话管理
```python
# 创建会话，设置过期时间
session_id = Session.create(username)
redis_client.set(session_key, data, ex=3600)
```

### 2. 任务列表排序
```python
# 使用有序集合按时间排序
redis_client.zadd(f'user:{username}:tasks', {task_id: timestamp})
task_ids = redis_client.zrevrange(tasks_key, 0, -1)  # 降序
```

### 3. 排行榜实现
```python
# 更新分数
redis_client.zincrby('leaderboard:completed_tasks', 1, username)
# 获取排名
rank = redis_client.zrevrank('leaderboard:completed_tasks', username)
```

### 4. 批量操作
```python
# 使用管道提高性能
pipe = redis_client.pipeline()
pipe.hset(key1, mapping=data1)
pipe.hset(key2, mapping=data2)
pipe.execute()
```

## 扩展功能建议

1. **任务分类和标签** - 使用 Redis Set 实现
2. **任务搜索** - 使用 Redis 全文搜索功能
3. **任务提醒** - 使用 Redis 过期键和通知
4. **数据导出** - 导出任务数据为 JSON/CSV
5. **任务分享** - 实现任务分享功能
6. **实时通知** - 使用 WebSocket + Redis Pub/Sub

## 常见问题

### Q: Redis 连接失败怎么办？
A: 确保 Redis 服务器正在运行：
```bash
./src/redis-server
```

### Q: 如何查看 Redis 中的数据？
A: 使用 redis-cli：
```bash
./src/redis-cli
> KEYS *
> HGETALL user:your_username
> HGETALL task:task_id
```

### Q: 如何清空所有数据？
A: 在 redis-cli 中执行：
```bash
FLUSHDB
```

## 下一步学习

1. 学习 Redis 持久化（RDB、AOF）
2. 学习 Redis 集群和主从复制
3. 学习 Redis 事务和 Lua 脚本
4. 学习 Redis Stream 实现消息队列
5. 学习 Redis 性能优化

## 参考资源

- [Redis 官方文档](https://redis.io/docs/)
- [Redis 命令参考](https://redis.io/commands/)
- [Flask 文档](https://flask.palletsprojects.com/)

祝你学习愉快！🚀

