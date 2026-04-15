# AGENTS.md — Pyxel Rogue

「過剰にオーバースペックな Pyxel 版・元祖ローグ」。ASCII ベースで Rogue 5.4 準拠を目指す。Pyxel 版をクリアしたら、それは本物の Rogue 5.4 をクリアしたと言える状態を最終目標にする。

- フレームワーク: Pyxel 2.9.0 / Python 3.10+
- 実行対象: Python/Pyxel 本体に加えて Pyxel Web も視野に入れる
- 想定環境: ブラウザ、デスクトップ、SteamDeck、中華ゲーム機など
- 現行本体: `rogue.py`
- タスク一覧は `TODO.md`、設計判断の経緯は `DESIGN.md` を参照

## セットアップ

```bash
pip install pyxel
python3 rogue.py
```

## テスト

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

ロジックテストは Pyxel を mock して実行可能（手順は DESIGN.md 末尾に記載）。

## コード構造

現行実装は `rogue.py` が中心。

```
rogue.py
├── 定数・テーブル（POTIONS[12], SCROLLS[12], WEAPONS[9], ARMORS[8], BESTIARY[26]）
├── Room / Item / Monster / Player / IdentTable / DGen（ダンジョン生成）
└── Game（メイン: ステートマシン ST_PLAY/MENU/ITEM/DIR/STATUS/HELP/MAP/DEAD）
    ├── update: 入力 → upd_play / upd_menu / upd_item / upd_dir
    ├── draw:   draw_zoom → draw_mini → draw_stat → draw_msgs → オーバーレイ
    └── 各ステートに upd_xxx() と draw_xxx() が1対1で対応
```

単一ファイルは前提にしない。見通しがよく、Rogue 5.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。

## 画面・マップ

- 現行マップ: 48×24、3×3セクターグリッド
- 現行画面: 480×310
- これらは現在の実装値であり、固定仕様ではない
- ブラウザ、SteamDeck、中華ゲーム機で遊べることを重視し、画面サイズ変更時はレイアウト定数を一箇所で再計算できる設計に寄せる

## コーディング規約

- 定数 `UPPER_SNAKE`、クラス `PascalCase`、メソッド `snake_case`（短縮可: `msg`, `txt`, `kp`）
- カテゴリ: `CAT_POT`, `CAT_SCR`, `CAT_WPN`, `CAT_ARM`, `CAT_FOOD`, `CAT_GOLD`
- **データ駆動**: 新要素はテーブル追加で対応。コード分岐は最小限
- 全テキスト描画は `self.txt(x, y, s, col)` 経由
- 原作 Rogue 5.4 と照合しやすいよう、ゲームロジックと表示・入力処理の責務を混ぜすぎない

## 操作方針

- 基本操作は A/B/Start/Select + D-pad を中心にする
- D-pad: 通常は8方向移動
- Start短押し: 「斜め補助モード」と「8方向移動モード（通常モード）」をトグル
- 斜め補助モード中のD-padは、左上=NW、右上=NE、右下=SE、左下=SW の同時押しだけを受け付ける。上下左右単体は移動しない
- 斜め補助モード ON/OFF は右側ステータス欄に表示する
- Start長押し依存は禁止（携帯機側の電源OFF等に割り当てられることがあるため）
- Select(Back): 補助メニュー（Map / Status / Help / Search）
- A: 決定 / 拾う / 階段
- B: 短押しでメニュー/キャンセル、長押し+方向でダッシュ。ダッシュ後に離した瞬間の短押し誤発火を避ける
- X/Y/L/R: 当面は必須操作に割り当てない。将来のショートカット予約
- `btn()`=ホールド、`btnp()`=ワンショット。単押しと長押しの競合に注意する

## 技術要点

- フォント標準: `pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__), "examples", "assets", "umplus_j10r.bdf"))`
- `umplus_j10r.bdf` は ASCII 6px、CJK 10px、日本語対応
- 将来的なフォント選択は許容する。ただし ASCII ローグ表示に向く可読性を必須条件にする
- カメラ: デッドゾーン方式。現行値は `DEAD_ZONE = 5` だが、追従開始が遅いので調整対象
- ダッシュ: B長押し＋方向を中心候補にする。壁・敵・ドア・分岐・階段で自動停止
- ダンジョン生成: Rogue 5.4 の C ソース確認を優先し、推測で似せない。通路生成は `do_passages()`, `conn()`, `door()`, `putpass()` の責務分担と比較できる形を保つ

## 禁止・注意事項

- Rogue 5.4 にない要素を追加しない（バージョン選択機能で対応予定）
- 解像度変更時はレイアウト定数を全て再計算すること
- マップ本体は ASCII ローグライク描画を保つ
- Pyxel Web で動かすことを前提に、デスクトップ固有の挙動へ依存しすぎない
