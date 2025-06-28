// static/js/dashboard.js - 最適化版

document.addEventListener('DOMContentLoaded', function() {
    // ローディング表示
    showLoading();
    
    // APIからデータを取得（タイムアウト設定付き）
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒でタイムアウト
    
    fetch('/api/dashboard', {
        signal: controller.signal,
        headers: {
            'Cache-Control': 'no-cache'
        }
    })
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error('データの取得に失敗しました');
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            
            // 統計情報を更新
            updateStats(data.stats);
            
            // グラフを並列で作成（パフォーマンス向上）
            Promise.all([
                createDailyChart(data.daily),
                createTagsChart(data.tags),
                createWeeklyChart(data.weekly || { labels: [], data: [] }),
                createMonthlyChart(data.monthly || { labels: [], data: [] })
            ]).catch(error => {
                console.error('グラフ作成エラー:', error);
            });
        })
        .catch(error => {
            hideLoading();
            console.error('データの取得に失敗しました:', error);
            showError('データの読み込みに失敗しました。ページを再読み込みしてください。');
        });
});

// ローディング表示
function showLoading() {
    // 各グラフエリアにローディング表示
    const canvases = document.querySelectorAll('canvas');
    canvases.forEach(canvas => {
        const parent = canvas.parentElement;
        if (!parent.querySelector('.loading-spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner text-center my-5';
            spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            parent.insertBefore(spinner, canvas);
            canvas.style.display = 'none';
        }
    });
}

// ローディング非表示
function hideLoading() {
    document.querySelectorAll('.loading-spinner').forEach(spinner => spinner.remove());
    document.querySelectorAll('canvas').forEach(canvas => {
        canvas.style.display = 'block';
    });
}

// エラー表示
function showError(message) {
    const container = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.insertBefore(alert, container.firstChild);
}

// 統計情報の更新
function updateStats(stats) {
    const updates = [
        { id: 'total-hours', value: stats.total_hours + '時間' },
        { id: 'total-logs', value: stats.total_logs + '件' },
        { id: 'avg-duration', value: stats.avg_duration + '分' },
        { id: 'total-tags', value: stats.total_tags + '個' }
    ];
    
    updates.forEach(update => {
        const element = document.getElementById(update.id);
        if (element) {
            element.textContent = update.value;
        }
    });
}

// Chart.js のデフォルト設定
Chart.defaults.animation.duration = 500; // アニメーション時間を短縮

// 日別学習時間チャート（簡略化）
function createDailyChart(data) {
    const ctx = document.getElementById('chart-daily');
    if (!ctx || !data.labels || data.labels.length === 0) return;
    
    return new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: '学習時間（分）',
                data: data.data,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                pointRadius: 2, // ポイントを小さく
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.parsed.y}分`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => value + '分'
                    }
                }
            }
        }
    });
}

// タグシェアチャート（簡略化）
function createTagsChart(data) {
    const ctx = document.getElementById('chart-tags');
    if (!ctx || !data.labels || data.labels.length === 0) return;
    
    return new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// 週別・月別チャート（簡略化された共通関数）
function createBarChart(canvasId, data, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data.labels || data.labels.length === 0) return;
    
    return new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: '学習時間（分）',
                data: data.data,
                backgroundColor: color + '33', // 透明度を追加
                borderColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => value + '分'
                    }
                }
            }
        }
    });
}

// 週別学習時間チャート
function createWeeklyChart(data) {
    return createBarChart('chart-weekly', data, '#36A2EB');
}

// 月別学習時間チャート
function createMonthlyChart(data) {
    return createBarChart('chart-monthly', data, '#FF6384');
}