#!/bin/bash
# Redis 任务管理系统启动脚本

echo "=========================================="
echo "Redis 任务管理系统启动脚本"
echo "=========================================="

# 检查 Redis 是否运行
echo "检查 Redis 连接..."
cd /home/knight/code/redis
if ./src/redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis 服务器正在运行"
else
    echo "✗ Redis 服务器未运行"
    echo "正在启动 Redis 服务器..."
    ./src/redis-server --daemonize yes
    sleep 2
    if ./src/redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis 服务器启动成功"
    else
        echo "✗ Redis 服务器启动失败，请手动启动"
        echo "运行: ./src/redis-server"
        exit 1
    fi
fi

# 检查 Python 依赖
echo ""
echo "检查 Python 依赖..."
cd /home/knight/code/redis/todo_app

# 尝试使用虚拟环境（如果存在）
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "使用虚拟环境..."
    source venv/bin/activate
elif [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "安装依赖..."
    pip install -r requirements.txt
else
    echo "虚拟环境存在但无法激活，使用系统 Python"
fi

# 检查依赖是否已安装
if ! pip show flask > /dev/null 2>&1; then
    echo "安装依赖..."
    pip install -r requirements.txt
else
    echo "✓ 依赖已安装"
fi

# 启动应用
echo ""
echo "启动 Flask 应用..."
echo "访问 http://localhost:5000"
echo ""
python3 app.py

