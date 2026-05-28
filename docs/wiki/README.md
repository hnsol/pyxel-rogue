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
- `Game-Guide-*.md`: ゲーム本体のテーブルから生成する攻略情報
- `Keyboard-Commands-*.md`: Rogue 5.4.4 / Rogue V5 on Pyxel / gamepad の操作対応表
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

## 攻略ページ生成

攻略ページは本体 repo で生成する。

```bash
python3 tools/generate_wiki.py
```

出力先は `wiki/`。`wiki/` が GitHub Wiki repo として clone 済みなら、その作業ツリーに `Game-Guide-ja.md` / `Game-Guide-en.md` / `Home.md` / `_Sidebar.md` が書き出される。未作成の場合も、同じパスにファイルを生成する。

モンスター出現率は Rogue 5.4.4 `randmonster()` 相当の理論値で計算する。モンテカルロ実行は使わない。

## Proximity Message Log

仕様の正本は `../DESIGN.md` と実装。wiki では、忠実性を損なわない移植UIとしての意義、視線設計、先行事例との距離を説明する。

## 保存資料

外部資料を repo に保存する場合は、出所、取得経路、保存日、ハッシュ、利用範囲を同じディレクトリの `README.md` に記録する。本文では長い逐語引用を避け、要約中心で使う。

`docs/sources/history-of-rogue/HistoryOfRogue.txt` は `Yozvox, HistoryOfRogue.txt` の保存コピーとして扱う。Rogue 受容史、版分岐、日本語圏での整理の二次資料であり、Rogue 5.4.4 のゲームメカニクスの一次資料ではない。
