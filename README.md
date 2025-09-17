# Auto Proxy Manager

一个简单的 Python 工具，用于自动测试免费 HTTP 代理列表，选择延迟最低的可用代理，并通过 Web 界面或状态文件提供该信息。

## 功能

*   **代理测速**: 定期测试 `proxies.json` 中列出的 HTTP 代理。
*   **自动选择**: 根据测试结果自动选择延迟最低的可用代理。
*   **状态输出**: 将最佳代理信息写入 `proxy_status.json` 文件。
*   **Web 界面**: 提供一个简单的 Web 界面来查看最佳代理和最近的测试结果。
*   **Cloudflare Tunnel 支持**: 包含脚本以使用 Cloudflare Quick Tunnels 暴露 Web 界面（适用于无公网 IP 的服务器）。
*   **Systemd 服务**: 提供 Systemd 服务文件以实现后台自动运行。

## 文件结构

*   `proxy_selector.py`: 核心测速和选择脚本。
*   `proxies.json`: 待测试的 HTTP 代理列表 (JSON 格式)。
*   `proxy_status.json`: 脚本生成的当前最佳代理和测试结果 (JSON 格式)。
*   `web_interface.py`: 提供 Web 界面的 Flask 应用。
*   `requirements.txt`: Python 依赖项列表。
*   `start_with_tunnel.sh`: (可选) 启动 Flask 应用和 Cloudflare Quick Tunnel 的脚本。
*   `systemd/auto-proxy-selector.service`: Systemd 服务配置文件。

## 安装与运行

### 1. 克隆仓库

bash
git clone <your-repo-url>
cd auto-proxy-manager


### 2. 安装依赖

确保你已经安装了 Python 3 和 pip。

bash
pip install -r requirements.txt


### 3. 配置代理列表

编辑 `proxies.json` 文件，添加或修改你想要测试的 HTTP 代理地址。

### 4. 运行代理选择器

可以直接运行脚本：

bash
python3 proxy_selector.py


或者，安装为 Systemd 服务以实现后台自动运行（见下方）。

### 5. 运行 Web 界面

bash
python3 web_interface.py


Web 界面默认运行在 `http://localhost:5000`。

### 6. (可选) 使用 Cloudflare Quick Tunnel

如果你的服务器没有公网 IP，可以使用 `start_with_tunnel.sh` 脚本。

1.  确保已安装 `cloudflared`。
2.  修改 `start_with_tunnel.sh` 中的路径。
3.  赋予脚本执行权限：`chmod +x start_with_tunnel.sh`
4.  运行脚本：`./start_with_tunnel.sh`
5.  脚本会输出一个临时的公共 URL，通过该 URL 可访问 Web 界面。

### 7. 安装为 Systemd 服务

1.  修改 `systemd/auto-proxy-selector.service` 文件中的 `User`, `WorkingDirectory`, 和 `ExecStart` 路径。
2.  将服务文件复制到 Systemd 目录：
    bash
    sudo cp systemd/auto-proxy-selector.service /etc/systemd/system/
    
3.  重新加载 Systemd 配置：
    bash
    sudo systemctl daemon-reload
    
4.  启用并启动服务：
    bash
    sudo systemctl enable auto-proxy-selector.service
    sudo systemctl start auto-proxy-selector.service
    
5.  检查服务状态：
    bash
    sudo systemctl status auto-proxy-selector.service
    

## 配置

可以在 `proxy_selector.py` 和 `web_interface.py` 的顶部找到可配置的参数，例如测试 URL、超时时间、测试间隔等。




