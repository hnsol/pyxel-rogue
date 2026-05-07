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
- `Playable-Critical-Edition.md`: 学術調の設計本文
- `Critical-Edition-Outline.md`: 章立てと執筆計画
- `Descend-Again.md`: 宣伝調の紹介本文
- `Editorial-Notes.md`: wiki 内の編集方針

## 文体

`Playable-Critical-Edition.md` は、冗談を本文へ混ぜない。学術文体を真剣に維持し、その過剰な真剣さを面白さにする。

`Descend-Again.md` は別ページに分離し、キャッチコピー、宣伝文句、勢いのある比喩を許可する。
