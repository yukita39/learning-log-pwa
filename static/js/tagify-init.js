// static/js/tagify-init.js
document.addEventListener("DOMContentLoaded", () => {
  const input  = document.querySelector('#tags-input');
  const tagify = new Tagify(input);

  // 既存タグ一覧を取得してホワイトリスト化
  fetch('/tags/suggest').then(r => r.json()).then(list => {
    tagify.settings.whitelist = list;

    // 上位 5 件ボタン生成
    const holder = document.getElementById('quick-tags');
    list.slice(0, 5).forEach(tag => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
      btn.textContent = tag;
      btn.onclick = () => tagify.addTags([tag]);
      holder.appendChild(btn);
    });
  });
});
