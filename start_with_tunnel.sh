#!/bin/bash

# --- 配置 ---
FLASK_APP_SCRIPT="web_interface.py" # 相对于脚本所在目录的 Flask 应用脚本
FLASK_HOST="127.0.0.1"              # Flask 绑定地址
FLASK_PORT="5000"                   # Flask 监听端口
# --- 配置结束 ---

# 获取脚本所在目录，确保路径正确
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FLASK_APP_PATH="$SCRIPT_DIR/$FLASK_APP_SCRIPT"

# 检查 Flask 应用脚本是否存在
if [[ ! -f "$FLASK_APP_PATH" ]]; then
    echo "错误: 找不到 Flask 应用脚本 '$FLASK_APP_PATH'"
    exit 1
fi

# 启动 Flask 应用 (在后台)
echo "启动 Flask 应用 ($FLASK_APP_SCRIPT)..."
export FLASK_APP="$FLASK_APP_PATH"
# 使用 nohup 和 & 将 Flask 放到后台运行，并将输出重定向到 flask.log
nohup flask run --host="$FLASK_HOST" --port="$FLASK_PORT" > "$SCRIPT_DIR/flask.log" 2>&1 &
FLASK_PID=$!
echo "Flask 应用 PID: $FLASK_PID"

# 等待几秒确保 Flask 启动
echo "等待 Flask 应用启动..."
sleep 5

# 检查 Flask 进程是否仍在运行
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "错误: Flask 应用启动失败。请检查 $SCRIPT_DIR/flask.log 获取详细信息。"
    exit 1
fi

# 启动 Cloudflared Quick Tunnel
echo "启动 Cloudflared Quick Tunnel..."
echo "请访问下方显示的临时 URL 来访问 Web 界面。"
echo "------------------------------------------------------------------------"
cloudflared tunnel --url "http://$FLASK_HOST:$FLASK_PORT"

# 如果 cloudflared 停止，也停止 Flask 应用
echo -e "\nCloudflared 已停止，正在关闭 Flask 应用 (PID: $FLASK_PID)..."
kill $FLASK_PID 2>/dev/null
wait $FLASK_PID 2>/dev/null
echo "Flask 应用已关闭。"




