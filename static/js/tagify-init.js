// static/js/tagify-init.js - リファクタリング版

/**
 * タグ入力システムの初期化と管理
 */
class TagManager {
    constructor() {
        this.tagify = null;
        this.inputElement = null;
        this.quickTagsContainer = null;
        this.popularTags = [];
    }

    /**
     * 初期化処理
     */
    async init() {
        try {
            // DOM要素の取得
            this.inputElement = document.querySelector("#tags-input");
            this.quickTagsContainer = document.getElementById("quick-tags");

            if (!this.inputElement) {
                console.warn("タグ入力欄が見つかりません");
                return;
            }

            // Tagifyの初期化
            this.initTagify();

            // フォーム送信イベントの設定
            this.setupFormSubmit();

            // 人気タグの読み込みと表示
            await this.loadPopularTags();

        } catch (error) {
            console.error("TagManager初期化エラー:", error);
        }
    }

    /**
     * Tagifyの初期化
     */
    initTagify() {
        // 既存のインスタンスがあれば破棄
        if (this.inputElement.tagify) {
            this.inputElement.tagify.destroy();
            delete this.inputElement.tagify;
        }

        // Tagifyの設定
        const tagifySettings = {
            placeholder: "タグを入力...",
            delimiters: ",|、| ",  // カンマ、日本語の読点、スペースで区切る
            maxTags: 10,           // 最大タグ数
            dropdown: {
                maxItems: 20,
                classname: "tags-dropdown",
                enabled: 0,
                closeOnSelect: false
            },
            originalInputValueFormat: values => values.map(item => item.value).join(", "),
            enforceWhitelist: false,  // 自由入力を許可
            callbacks: {
                add: this.onTagAdd.bind(this),
                remove: this.onTagRemove.bind(this)
            }
        };

        // Tagifyインスタンスの作成
        this.tagify = new Tagify(this.inputElement, tagifySettings);
        this.inputElement.tagify = this.tagify;
    }

    /**
     * タグ追加時のコールバック
     */
    onTagAdd(e) {
        console.log("タグ追加:", e.detail.data.value);
        this.updateQuickTagButtons();
    }

    /**
     * タグ削除時のコールバック
     */
    onTagRemove(e) {
        console.log("タグ削除:", e.detail.data.value);
        this.updateQuickTagButtons();
    }

    /**
     * フォーム送信時の処理
     */
    setupFormSubmit() {
        const form = this.inputElement.closest("form");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            // Tagifyの値を通常のカンマ区切り文字列に変換
            const tagValues = this.tagify.value.map(item => item.value);
            this.inputElement.value = tagValues.join(", ");
            
            console.log("送信するタグ:", this.inputElement.value);
        });
    }

    /**
     * 人気タグの読み込み
     */
    async loadPopularTags() {
        try {
            // ローディング表示
            if (this.quickTagsContainer) {
                this.quickTagsContainer.innerHTML = '<span class="text-muted">読み込み中...</span>';
            }

            // APIから人気タグを取得（エンドポイントを修正）
            const response = await fetch("/api/popular-tags");
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // データ形式の処理（APIが配列またはオブジェクト配列を返す場合に対応）
            if (Array.isArray(data)) {
                // [{tag: "Python", count: 5}, ...] の形式の場合
                if (data.length > 0 && typeof data[0] === 'object' && 'tag' in data[0]) {
                    this.popularTags = data;
                } 
                // ["Python", "Flask", ...] の形式の場合
                else if (typeof data[0] === 'string') {
                    this.popularTags = data.map(tag => ({ tag, count: 0 }));
                }
            }

            // Tagifyのホワイトリストを更新
            if (this.popularTags.length > 0) {
                this.tagify.settings.whitelist = this.popularTags.map(item => item.tag);
            }

            // クイックタグボタンを表示
            this.displayQuickTags();

        } catch (error) {
            console.error("人気タグの取得に失敗:", error);
            if (this.quickTagsContainer) {
                this.quickTagsContainer.innerHTML = 
                    '<small class="text-danger">タグの読み込みに失敗しました</small>';
            }
        }
    }

    /**
     * クイックタグボタンの表示
     */
    displayQuickTags() {
        if (!this.quickTagsContainer) return;

        this.quickTagsContainer.innerHTML = "";

        if (this.popularTags.length === 0) {
            this.quickTagsContainer.innerHTML = 
                '<small class="text-muted">まだタグが登録されていません</small>';
            return;
        }

        // 上位タグをボタンとして表示
        const maxTags = Math.min(this.popularTags.length, 8); // 最大8個まで表示
        
        for (let i = 0; i < maxTags; i++) {
            const tagData = this.popularTags[i];
            const button = this.createTagButton(tagData);
            this.quickTagsContainer.appendChild(button);
        }

        // 初期状態のボタン更新
        this.updateQuickTagButtons();
    }

    /**
     * タグボタンの作成
     */
    createTagButton(tagData) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-sm btn-outline-primary me-1 mb-1";
        button.dataset.tag = tagData.tag;
        
        // ボタンのテキスト（使用回数がある場合は表示）
        if (tagData.count > 0) {
            button.innerHTML = `
                <i class="fas fa-tag"></i> 
                ${tagData.tag} 
                <span class="badge bg-primary">${tagData.count}</span>
            `;
        } else {
            button.innerHTML = `<i class="fas fa-tag"></i> ${tagData.tag}`;
        }

        // クリックイベント
        button.addEventListener("click", () => {
            this.addTag(tagData.tag);
        });

        return button;
    }

    /**
     * タグの追加
     */
    addTag(tag) {
        // 既に追加されているかチェック
        const currentTags = this.tagify.value.map(item => item.value);
        
        if (currentTags.includes(tag)) {
            // 既に存在する場合はハイライト効果
            this.highlightExistingTag(tag);
        } else {
            // タグを追加
            this.tagify.addTags([tag]);
        }
    }

    /**
     * 既存タグのハイライト
     */
    highlightExistingTag(tag) {
        const tagElements = this.tagify.getTagElms();
        const targetTag = tagElements.find(el => 
            el.querySelector('.tagify__tag-text').textContent === tag
        );
        
        if (targetTag) {
            targetTag.style.animation = 'pulse 0.5s';
            setTimeout(() => {
                targetTag.style.animation = '';
            }, 500);
        }
    }

    /**
     * クイックタグボタンの状態更新
     */
    updateQuickTagButtons() {
        if (!this.quickTagsContainer) return;

        const currentTags = this.tagify.value.map(item => item.value);
        const buttons = this.quickTagsContainer.querySelectorAll('button');

        buttons.forEach(button => {
            const tag = button.dataset.tag;
            if (currentTags.includes(tag)) {
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-primary');
                button.disabled = false; // 重複追加を防ぐ場合は true に
            } else {
                button.classList.remove('btn-primary');
                button.classList.add('btn-outline-primary');
                button.disabled = false;
            }
        });
    }
}

// CSSアニメーションの追加
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .tags-dropdown {
        z-index: 9999;
    }
    
    .tagify {
        min-height: 42px;
    }
    
    .tagify__tag {
        margin: 2px;
    }
`;
document.head.appendChild(style);

// DOMContentLoaded時に初期化
document.addEventListener("DOMContentLoaded", () => {
    const tagManager = new TagManager();
    tagManager.init();
    
    // グローバルに公開（デバッグ用）
    window.tagManager = tagManager;
});