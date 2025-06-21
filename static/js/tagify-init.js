//  static/js/tagify-init.js
console.log("▶ tagify-init.js loaded");
document.addEventListener("DOMContentLoaded", async () => {
  const el = document.querySelector("#tags-input");
  if (!el) return;

  /* --- ① 旧インスタンスがあれば完全破棄 --- */
  if (el.tagify) {
    el.tagify.destroy();   // イベント & DOM クリーンアップ
    delete el.tagify;      // ← これが肝心！
  }

  /* --- ② 正しい設定で再生成 --- */
  const tagify = new Tagify(el, {
    originalInputValueFormat: arr => arr.map(x => x.value).join(","),  // "Python,Flask"
    enforceWhitelist: false,   // 手入力を許可
  });

  /* --- ③ 人気タグ取得 → ホワイトリスト & ボタン --- */
  try {
    const res  = await fetch("/tags/suggest");
    const list = await res.json();         // 例 ["Python","Flask"]

    tagify.settings.whitelist = list;

    const holder = document.getElementById("quick-tags");
    holder.innerHTML = "";                 // 二重生成防止
    list.slice(0, 5).forEach(tag => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "btn btn-sm btn-outline-secondary me-1 mb-1";
      b.textContent = tag;
      b.onclick = () => tagify.addTags([tag]);
      holder.appendChild(b);
    });
  } catch (e) {
    console.error("タグ候補取得失敗:", e);
  }
});
