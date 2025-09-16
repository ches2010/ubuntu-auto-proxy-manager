#!/bin/bash

# --- 配置 ---
FLASK_APP_PATH="/home/your_username/auto-proxy-manager/web_interface.py" # 请修改为你的实际路径
FLASK_HOST="127.0.0.1" # 绑定到本地
FLASK_PORT=5000
# --- 配置结束 ---

# 启动 Flask 应用 (在后台)
echo "启动 Flask 应用..."
export FLASK_APP=$FLASK_APP_PATH
nohup flask run --host=$FLASK_HOST --port=$FLASK_PORT > flask.log 2>&1 &
FLASK_PID=$!
echo "Flask 应用 PID: $FLASK_PID"

# 等待几秒确保 Flask 启动
sleep 5

# 启动 Cloudflared Quick Tunnel
echo "启动 Cloudflared Quick Tunnel..."
cloudflared tunnel --url http://$FLASK_HOST:$FLASK_PORT

# 如果 cloudflared 停止，也停止 Flask 应用
echo "Cloudflared 已停止，正在关闭 Flask 应用..."
kill $FLASK_PID 2>/dev/null
wait $FLASK_PID 2>/dev/null
echo "Flask 应用已关闭。"



