# Design: call_it() + print_disc()

Date: 2026-04-24  
Ref: `vendor/rogue544/misc.c:call_it()`, `vendor/rogue544/things.c:print_disc()`  
TODO: Phase 4 鑑定・命名・発見リスト忠実度

## Overview

- `call_it()` — `C` キーでアイテムに仮名（`oi_guess`）を付ける。`misc.c:call_it()` 準拠。
- `print_disc()` — `D` キーで発見済みアイテム一覧を表示。`things.c:print_disc()` の `*`（全カテゴリ）相当。

---

## New States

```python
ST_CALL = 13   # call_it: アイテム選択 → テキスト入力
ST_DISC = 14   # print_disc: 発見リスト表示
```

---

## call_it() フロー

### ステート遷移

```
upd_play: C key
  → fitems = ポーション/巻物/指輪/杖でフィルタ（oi_know 済みは除外しない）
  → cact = "Call", st = ST_CALL（選択段階）
  → アイテム確定 (A)
  → call_input = "" (or preset[0]), call_preset_idx = 0, st = ST_CALL（入力段階）
  → 確定 (Enter/A) → ident.pg/sg/rg/wg[kind] に保存, ST_PLAY（ターン消費なし）
  → キャンセル (Esc/B) → ST_PLAY
```

### 原作準拠の保存ロジック（misc.c:call_it()）

- `oi_know` が True の場合: `oi_guess` をクリア（仮名不要）してそのまま返る
- `oi_know` が False で `oi_guess` が既存の場合: 上書き確認なしで上書き
- 空文字列 Enter: 既存 `oi_guess` をクリア

### 入力受付

| 入力 | 動作 |
|---|---|
| ↑↓ (gamepad/keyboard) | `CALL_PRESETS` を循環、`call_input` を更新 |
| `KEY_A`〜`KEY_Z`, `KEY_SPACE` | キーボード文字追加（最大16文字）、プリセット選択を解除 |
| `KEY_BACKSPACE` | 末尾1文字削除 |
| Enter / A ボタン | 確定 |
| Esc / B ボタン | キャンセル |

### プリセット定数

```python
CALL_PRESETS = [
    "good", "bad",  "meh",  "skip",
    "try",  "use",  "id?",  "boo",
    "zap",  "hmm",  "ugh",  "yay",
    "wow",  "odd",  "???",  "!!!",
]
```

### draw_call_input（新規）

選択段階: `draw_isel` を流用。  
入力段階: 小さいボックスを1つ追加表示。

```
+---------------------------+
| what do you want to call  |
| it? > good_              |
| [↑↓ preset / type / Enter]|
+---------------------------+
```

---

## print_disc() フロー

### ステート遷移

```
upd_play: D key
  → disc_scroll = 0, st = ST_DISC
  → ↑↓ で disc_scroll を操作
  → A / B / Esc で ST_PLAY（ターン消費なし）
```

### 表示内容（draw_disc 新規）

全カテゴリを縦に列挙。`oi_know` または `oi_guess` のあるものだけ表示。

```
=== Discoveries ===
-- Potions --
red potion of haste
blue potion called boo
-- Scrolls --
(nothing discovered)
-- Rings --
...
-- Sticks --
...
```

- `inv_name` 相当は既存 `ident.name(it)` を使い、ダミー `Item` を生成して表示
- スクロール: `disc_scroll` オフセット、1行=9px、表示可能行数は描画エリアから算出

### TextCatalog 追加

- `"pyxel.what_to_call_it"` → `"what do you want to call it? "` / `「名前をつける：」`
- `"pyxel.discoveries_title"` → `"Discoveries"` / `「発見リスト」`
- `"pyxel.nothing_discovered"` → `"(nothing discovered)"` / `「（未発見）」`
- カテゴリ見出し: `"Potions"/"Scrolls"/"Rings"/"Sticks"` → 既存 `TextCatalog.item_kind` か新規

---

## 入力トリガー

`rogue_command_action()` に追加:

```python
if self.key_lower(pyxel.KEY_C): return "Call"
if self.key_upper(pyxel.KEY_D): ...  # D は upd_play 直接処理（アイテム選択不要）
```

`C` は `start_item_action("Call")` 経由で ST_CALL へ。  
`D` は `upd_play` で直接 `ST_DISC` へ遷移。

---

## ターン消費

- `call_it`: ターン消費なし（原作 `misc.c:call_it()` はターン消費しない）
- `print_disc`: ターン消費なし

---

## テスト

- `IdentTable.pg/sg/rg/wg` への書き込みと読み出しが `ident.name()` に反映される
- `oi_know` 済みアイテムを Call すると `oi_guess` がクリアされる
- 空文字確定で `oi_guess` がクリアされる
- `print_disc` が `oi_know` / `oi_guess` のあるアイテムだけ列挙する
