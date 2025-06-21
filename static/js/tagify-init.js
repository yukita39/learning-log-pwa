// static/js/tagify-init.js
document.addEventListener("DOMContentLoaded", async () => {
  const input = document.querySelector("#tags-input");
  if (!input) return;

  /***** ① すでに Tagified なら再設定だけ行う *****/
  let tagify = input.tagify || new Tagify(input);

  // 強制的に設定を上書き
  tagify.settings.originalInputValueFormat = v =>
    v.map(t => t.value).join(",");

  // 拡張が enforceWhitelist=true にしている場合に備え false に戻す
  tagify.settings.enforceWhitelist = false;

  /***** ② 人気タグを取得してホワイトリスト & ボタン作成 *****/
  try {
    const res  = await fetch("/tags/suggest");
    const list = await res.json();          // ["Python", "Flask", …]

    tagify.settings.whitelist = list;

    const holder = document.getElementById("quick-tags");
    holder.innerHTML = "";                  // 二重生成ガード
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