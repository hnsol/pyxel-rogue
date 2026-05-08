# Wiki 運用メモ

GitHub Wiki は本体 repo と別 git repo として扱う。

## 方針

- ローカル作業場所は repo root の `wiki/`
- `wiki/` は `.gitignore` 対象
- wiki 本文は GitHub Wiki repo にのみ置く
- 本体 repo には、この運用メモだけ残す

## 初回

GitHub の Wiki タブで最初のページを作り、Wiki repo を有効化する。

```bash
git clone git@github.com:hnsol/pyxel-rogue.wiki.git wiki
```

すでに `wiki/` を作ってある場合:

```bash
cd wiki
git remote -v
git push -u origin master
```

## ページ構成

- `Home.md`: 入口
- `_Sidebar.md`: GitHub Wiki のサイドバー
- 接尾辞なしの各ページ: 日英の言語選択
- `*-ja.md`: 日本語本文
- `*-en.md`: 英語本文
- `Playable-Critical-Edition-*.md`: 学術調の設計本文
- `Critical-Edition-Outline-*.md`: 章立てと執筆計画
- `Proximity-Message-Log-*.md`: 近接メッセージログの設計説明
- `Descend-Again-*.md`: 宣伝調の紹介本文
- `Editorial-Notes.md`: wiki 内の編集方針

## 日英運用

日本語を正本として先に育てる。英語版は同じ構成を保つが、逐語訳である必要はない。未完成の場合も、空白にせず短い要約と `TODO` を置く。

## 文体

`Playable-Critical-Edition.md` は、冗談を本文へ混ぜない。学術文体を真剣に維持し、その過剰な真剣さを面白さにする。

`Descend-Again.md` は別ページに分離し、キャッチコピー、宣伝文句、勢いのある比喩を許可する。

## Proximity Message Log

仕様の正本は `DESIGN.md` と実装。wiki では、忠実性を損なわない移植UIとしての意義、視線設計、先行事例との距離を説明する。
