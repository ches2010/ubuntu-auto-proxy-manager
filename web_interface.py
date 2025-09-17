#!/usr/bin/env python3

from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# --- 配置 ---
STATUS_FILE = "proxy_status.json"
# --- 配置结束 ---

# --- HTML 模板 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Auto Proxy Manager</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
        .container { background-color: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        h1 { color: #333; }
        .status { margin-bottom: 20px; padding: 15px; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        pre { background-color: #f8f9fa; padding: 15px; border: 1px solid #e9ecef; border-radius: 4px; white-space: pre-wrap; }
        .refresh-info { font-size: 0.9em; color: #6c757d; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Auto Proxy Manager</h1>
        <div class="status {{ 'success' if data.best_proxy else 'error' }}">
            <strong>状态:</strong>
            {% if data.best_proxy %}
                <p>最优代理: <code>{{ data.best_proxy.url }}</code> (延迟: {{ data.best_proxy.delay }} ms)</p>
                <p>更新时间: {{ data.last_update }}</p>
            {% else %}
                <p>当前无可用代理。</p>
                <p>上次更新时间: {{ data.last_update }}</p>
            {% endif %}
        </div>

        <h2>最近测试结果</h2>
        <details>
            <summary>点击查看/隐藏</summary>
            <pre>{{ data.all_results | tojson(indent=2) }}</pre>
        </details>

        <div class="refresh-info">
            <p>此页面不会自动刷新。请手动刷新以获取最新状态。</p>
            <p><a href="/api/status">API 端点: /api/status</a></p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """主页，显示最佳代理信息和测试结果"""
    data = {}
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                data = json.load(f)
        else:
             data = {"error": f"状态文件 '{STATUS_FILE}' 不存在。请确保 proxy_selector.py 正在运行。"}
    except Exception as e:
        data = {"error": f"读取状态文件时出错: {str(e)}"}

    # 确保必要的键存在
    data.setdefault("last_update", "N/A")
    data.setdefault("best_proxy", None)
    data.setdefault("all_results", [])

    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/api/status')
def api_status():
    """API 端点，返回 JSON 格式的代理状态"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": f"状态文件 '{STATUS_FILE}' 不存在。"}), 404
    except Exception as e:
        return jsonify({"error": f"读取状态文件时出错: {str(e)}"}), 500

if __name__ == '__main__':
    # 注意：在生产环境中，不要使用 Flask 内置服务器。
    # 这里 host='0.0.0.0' 使其可以在网络上访问（如果防火墙允许）
    app.run(host='127.0.0.1', port=5000, debug=False)




