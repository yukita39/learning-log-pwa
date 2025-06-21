// static/js/tagify-init.js
document.addEventListener("DOMContentLoaded", async () => {
  const el = document.querySelector("#tags-input");
  if (!el) return console.warn("タグ入力欄が見つかりません");

  // ① 旧インスタンスがあれば完全破棄
  if (el.tagify) {
    el.tagify.destroy();
    delete el.tagify;
  }

  // ② 新しく Tagify を作成
  const tagify = new Tagify(el, {
    // カンマ区切りに変換するロジック
    originalInputValueFormat: arr => arr.map(x => x.value).join(","),
    // 自由入力を許可
    enforceWhitelist: false,
  });
  // 明示的に element にも保持しておく
  el.tagify = tagify;

  // ③ フォーム送信前に input.value を上書き
  const form = el.closest("form");
  if (form) {
    form.addEventListener("submit", () => {
      // tagify.value は [{value:"Python"},…]
      el.value = tagify.value.map(item => item.value).join(",");
    });
  }

  // ④ 人気タグを取得してホワイトリスト＆ボタン描画
  try {
    const res  = await fetch("/tags/suggest");
    const list = await res.json();  // ["Python","Flask",...]
    tagify.settings.whitelist = list;

    const holder = document.getElementById("quick-tags");
    holder.innerHTML = "";  // 既存ボタンをクリア
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