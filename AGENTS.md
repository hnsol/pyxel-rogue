# AGENTS.md — Pyxel Rogue

「過剰にオーバースペックな Pyxel 版・元祖ローグ」。ASCII ベース、Rogue 5.4 準拠を目指す Phase 3 実装。

- フレームワーク: Pyxel 2.9.0 / Python 3.10+ / デスクトップ専用
- 単一ファイル: `rogue.py`（1149行）
- タスク一覧は `TODO.md`、設計経緯は `DESIGN.md` を参照

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

```
rogue.py
├── 定数・テーブル（POTIONS[12], SCROLLS[12], WEAPONS[9], ARMORS[8], BESTIARY[26]）
├── Room / Item / Monster / Player / IdentTable / DGen（ダンジョン生成）
└── Game（メイン: ステートマシン ST_PLAY/MENU/ITEM/DIR/STATUS/HELP/MAP/DEAD）
    ├── update: 入力 → upd_play / upd_menu / upd_item / upd_dir
    ├── draw:   draw_zoom → draw_mini → draw_stat → draw_msgs → オーバーレイ
    └── 各ステートに upd_xxx() と draw_xxx() が1対1で対応
```

マップ: 48×24、3×3セクターグリッド。画面: 480×310。

## コーディング規約

- **単一ファイル維持**（データ ~500行超えたら分割可）
- 定数 `UPPER_SNAKE`、クラス `PascalCase`、メソッド `snake_case`（短縮可: `msg`, `txt`, `kp`）
- カテゴリ: `CAT_POT`, `CAT_SCR`, `CAT_WPN`, `CAT_ARM`, `CAT_FOOD`, `CAT_GOLD`
- **データ駆動**: 新要素はテーブル追加で対応。コード分岐は最小限
- 全テキスト描画は `self.txt(x, y, s, col)` 経由（BDF フォント使用）

## 技術要点

- フォント: `pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__), "examples", "assets", "umplus_j10r.bdf"))` — ASCII 6px、CJK 10px、日本語対応
- パッド: A/B/X/Y/L/R/Start/Back/D-pad 全使用可。`btn()`=ホールド、`btnp()`=ワンショット
- カメラ: デッドゾーン方式（端5タイルで追従、中央は不動）
- ダッシュ: B長押し＋方向。壁・敵・ドア・分岐・階段で自動停止

## 禁止事項

- Rogue 5.4 にない要素を追加しない（バージョン選択機能で対応予定）
- 解像度変更時はレイアウト定数を全て再計算すること
- BDF フォント以外に切り替えない
- `pyxel.image` / `tilemap` で描画しない（ASCII ローグライク）
- Pyxel Web を前提にしない
