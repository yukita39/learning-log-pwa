document.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch('/stats/data');
  const data = await res.json();

  // 棒グラフ: 日別学習時間
  const ctx1 = document.getElementById('chart-daily').getContext('2d');
  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: data.daily.map(x => x.date),
      datasets: [{
        label: '学習時間（分）',
        data: data.daily.map(x => x.duration),
      }]
    },
    options: {
      scales: {
        x: { title: { display: true, text: '日付' } },
        y: { title: { display: true, text: '合計時間 (分)' }, beginAtZero: true }
      }
    }
  });

  // 円グラフ: タグシェア
  const ctx2 = document.getElementById('chart-tags').getContext('2d');
  new Chart(ctx2, {
    type: 'pie',
    data: {
      labels: data.tag_share.map(x => x.tag),
      datasets: [{ data: data.tag_share.map(x => x.count) }]
    }
  });
});