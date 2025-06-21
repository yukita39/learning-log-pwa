// static/js/tagify-init.js  (フロントエンド側)
document.addEventListener("DOMContentLoaded", async () => {
  const input  = document.querySelector('#tags-input');
  if (!input) {
    console.error('タグ入力欄 (#tags-input) が見つかりません');
    return;
  }

  // Tagify 初期化
const tagify = new Tagify(input, {
  originalInputValueFormat: v => v.map(t => t.value).join(",")   // ←これ必須
});

  /* --- 人気タグ（トップ20）を取得しホワイトリストへ --- */
  try {
    const res  = await fetch('/tags/suggest');
    const list = await res.json();           // ["Python","Flask",...]

    tagify.settings.whitelist = list;

    // クイックタグボタン（上位5件）
    const holder = document.getElementById('quick-tags');
    list.slice(0, 5).forEach(tag => {
      const btn = document.createElement('button');
      btn.type      = 'button';
      btn.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
      btn.textContent = tag;
      btn.onclick  = () => tagify.addTags([tag]);
      holder.appendChild(btn);
    });
  } catch (err) {
    console.error('タグ候補の取得に失敗:', err);
  }
});