function fetchData() {
    fetch('/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应错误');
            }
            return response.json();
        })
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
window.addEventListener('load', fetchData);



