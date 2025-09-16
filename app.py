from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)
STATUS_FILE = "proxy_status.json" # 与 proxy_selector.py 保持一致

# --- 简单的 HTML 前端 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>自动代理选择器</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .best { background-color: #c8e6c9; font-weight: bold; } /* 绿色背景表示最优 */
        .error { color: red; }
        .slow { color: orange; }
        #refresh-btn { margin-bottom: 10px; padding: 5px 10px; }
    </style>
</head>
<body>
    <h1>自动代理选择器</h1>
    <button id="refresh-btn">刷新数据</button>
    <p><strong>最后更新时间:</strong> <span id="update-time">加载中...</span></p>
    <p><strong>当前最优代理:</strong> <span id="best-proxy">加载中...</span></p>
    
    <h2>代理列表</h2>
    <table id="proxy-table">
        <thead>
            <tr>
                <th>代理地址</th>
                <th>状态</th>
                <th>延迟 (ms)</th>
            </tr>
        </thead>
        <tbody>
            <!-- 数据将通过 JS 动态填充 -->
        </tbody>
    </table>

    <script>
        function fetchData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('update-time').textContent = data.last_update || '未知';
                    
                    const bestProxySpan = document.getElementById('best-proxy');
                    if (data.best_proxy && data.best_proxy.url) {
                        bestProxySpan.textContent = data.best_proxy.url;
                        bestProxySpan.className = '';
                    } else {
                        bestProxySpan.textContent = '无可用代理';
                        bestProxySpan.className = 'error';
                    }

                    const tableBody = document.querySelector('#proxy-table tbody');
                    tableBody.innerHTML = ''; // 清空现有数据

                    if (data.all_results && data.all_results.length > 0) {
                        data.all_results.forEach(proxy => {
                            const row = document.createElement('tr');
                            
                            const urlCell = document.createElement('td');
                            urlCell.textContent = proxy.url;
                            
                            const statusCell = document.createElement('td');
                            statusCell.textContent = proxy.status;
                            if (proxy.status !== 'ok') {
                                statusCell.className = proxy.status.startsWith('error') ? 'error' : 'slow';
                            }
                            
                            const delayCell = document.createElement('td');
                            delayCell.textContent = proxy.delay !== undefined ? proxy.delay : 'N/A';

                            row.appendChild(urlCell);
                            row.appendChild(statusCell);
                            row.appendChild(delayCell);
                            
                            // 如果是当前最优代理，则高亮
                            if (data.best_proxy && proxy.url === data.best_proxy.url) {
                                row.classList.add('best');
                            }
                            
                            tableBody.appendChild(row);
                        });
                    } else {
                        const row = document.createElement('tr');
                        const cell = document.createElement('td');
                        cell.colSpan = 3;
                        cell.textContent = '暂无数据';
                        cell.style.textAlign = 'center';
                        row.appendChild(cell);
                        tableBody.appendChild(row);
                    }
                })
                .catch(error => {
                    console.error('获取数据失败:', error);
                    document.getElementById('update-time').textContent = '加载失败';
                    document.getElementById('best-proxy').textContent = '加载失败';
                });
        }

        document.getElementById('refresh-btn').addEventListener('click', fetchData);
        
        // 页面加载完成后自动获取一次数据
        window.onload = fetchData;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    """API 端点，返回代理状态 JSON"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": f"读取状态文件失败: {str(e)}"}), 500
    else:
        return jsonify({"error": "状态文件未找到"}), 404

if __name__ == '__main__':
    # 注意：在生产环境中不要使用 app.run()，应使用 Gunicorn 或 uWSGI
    # 此处仅为演示和简单运行
    app.run(host='0.0.0.0', port=5000, debug=False) 




