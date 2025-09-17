#!/usr/bin/env python3

import requests
import time
import json
import sys
import os

# --- 配置 ---
PROXY_LIST_FILE = "proxies.json"  # 代理列表文件
TEST_URL = "http://www.gstatic.com/generate_204"
TIMEOUT = 10  # 秒
MAX_DELAY_MS = 10000  # 最大可接受延迟 (毫秒)
TEST_INTERVAL = 300  # 秒, 测试间隔
STATUS_FILE = "proxy_status.json"
# --- 配置结束 ---


# --- 加载代理列表 ---
def load_proxy_list():
    """从 JSON 文件加载代理列表"""
    global PROXY_LIST
    try:
        if not os.path.exists(PROXY_LIST_FILE):
             print(f"警告: 找不到代理列表文件 '{PROXY_LIST_FILE}'。将创建一个空列表。")
             PROXY_LIST = []
             # 创建一个空文件
             with open(PROXY_LIST_FILE, 'w') as f:
                 json.dump(PROXY_LIST, f, indent=4)
             return True

        with open(PROXY_LIST_FILE, 'r') as f:
            PROXY_LIST = json.load(f)
        if not isinstance(PROXY_LIST, list):
            raise ValueError(f"{PROXY_LIST_FILE} 文件内容必须是一个 JSON 数组。")
        print(f"成功从 {PROXY_LIST_FILE} 加载了 {len(PROXY_LIST)} 个代理。")
        return True # 表示加载成功
    except FileNotFoundError:
        print(f"错误: 找不到代理列表文件 '{PROXY_LIST_FILE}'。")
        return False
    except json.JSONDecodeError as e:
        print(f"错误: '{PROXY_LIST_FILE}' 文件格式不正确 (JSON 解析错误): {e}")
        return False
    except ValueError as e:
        print(f"错误: '{PROXY_LIST_FILE}' 文件内容无效: {e}")
        return False
    except Exception as e:
        print(f"加载代理列表时发生未知错误: {e}")
        return False


# --- 测试单个代理 ---
def test_proxy(proxy_url):
    """测试单个代理的延迟和可用性"""
    proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }
    start_time = time.time()
    try:
        response = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        end_time = time.time()
        delay_ms = int((end_time - start_time) * 1000)

        # 检查响应状态码和内容
        if response.status_code == 204 and len(response.content) == 0:
             return {
                'url': proxy_url,
                'status': 'success',
                'delay': delay_ms,
                'timestamp': time.time()
            }
        else:
            # 如果状态码不是204或有内容，也认为失败
            return {
                'url': proxy_url,
                'status': 'failed',
                'delay': None,
                'error': f"Unexpected response: {response.status_code}, Content-Length: {len(response.content)}",
                'timestamp': time.time()
            }
    except requests.exceptions.RequestException as e:
        # 捕获所有 requests 相关的异常
        end_time = time.time()
        delay_ms = int((end_time - start_time) * 1000)
        return {
            'url': proxy_url,
            'status': 'failed',
            'delay': delay_ms if delay_ms <= MAX_DELAY_MS else None, # 如果超时前有延迟，也记录
            'error': str(e),
            'timestamp': time.time()
        }
    except Exception as e:
        # 捕获其他可能的异常
        return {
            'url': proxy_url,
            'status': 'failed',
            'delay': None,
            'error': f"Unexpected error: {e}",
            'timestamp': time.time()
        }


# --- 选择最优代理 ---
def select_best_proxy(results):
    """从测试结果中选择延迟最低的成功代理"""
    successful_proxies = [r for r in results if r['status'] == 'success' and r['delay'] is not None and r['delay'] <= MAX_DELAY_MS]

    if not successful_proxies:
        return None

    # 按延迟排序，取第一个
    best_proxy = min(successful_proxies, key=lambda x: x['delay'])
    return best_proxy


# --- 主测试循环 ---
def run_tests():
    """主测试循环"""
    # 尝试加载代理列表
    if not load_proxy_list():
        print("无法加载代理列表，程序退出。")
        sys.exit(1)

    print("代理测速脚本启动...")
    while True:
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - 开始测试所有代理...")
        results = []
        # 为了简化和避免对代理服务器造成过大压力，这里使用串行测试。
        # 对于大量代理或需要更快测试周期的场景，可以考虑并发（如使用 concurrent.futures.ThreadPoolExecutor）。
        for proxy in PROXY_LIST:
             result = test_proxy(proxy)
             results.append(result)
             # 可选：打印每个代理的测试结果
             # print(f"  - {proxy}: {result['status']} (延迟: {result['delay']}ms)")

        best_proxy = select_best_proxy(results)

        # 准备写入文件的数据
        status_data = {
            "last_update": time.strftime('%Y-%m-%d %H:%M:%S'),
            "best_proxy": best_proxy,
            "all_results": results # 可选：保存所有结果供调试
        }

        # 写入文件
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(status_data, f, indent=4)
            print(f"  -> 最优代理: {best_proxy['url'] if best_proxy else 'None (无可用代理)'}")
        except Exception as e:
            print(f"  -> 写入状态文件 '{STATUS_FILE}' 失败: {e}")

        print(f"等待 {TEST_INTERVAL} 秒后进行下一次测试...")
        time.sleep(TEST_INTERVAL)


if __name__ == "__main__":
    run_tests()




