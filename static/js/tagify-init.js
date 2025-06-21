// static/js/tagify-init.js
document.addEventListener("DOMContentLoaded", async () => {
  const el = document.querySelector("#tags-input");
  if (!el) return;

  /* ① 既に Tagified なら完全に破棄して作り直す */
  if (el.tagify) {
    el.tagify.destroy();        // インスタンス & イベントを完全削除
  }

  /* ② 正しい設定で新しく生成 */
  const tagify = new Tagify(el, {
    originalInputValueFormat: v => v.map(t => t.value).join(","),  // ← 重要
    enforceWhitelist: false,
  });

  /* ③ 人気タグを取得してホワイトリスト & ボタン */
  try {
    const res  = await fetch("/tags/suggest");
    const list = await res.json();  // 例 ["Python","Flask",…]

    tagify.settings.whitelist = list;

    const holder = document.getElementById("quick-tags");
    holder.innerHTML = "";          // 二重生成防止
    list.slice(0, 5).forEach(tag => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-sm btn-outline-secondary me-1 mb-1";
      btn.textContent = tag;
      btn.onclick = () => tagify.addTags([tag]);
      holder.appendChild(btn);
    });
  } catch (err) {
    console.error("タグ候補取得失敗:", err);
  }
});
