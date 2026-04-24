# call_it() + print_disc() Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Rogue 5.4.4 `misc.c:call_it()` (仮名付け、`C` キー) と `things.c:print_disc()` (発見リスト、`D` キー) を Pyxel Rogue に追加する。

**Architecture:** `rogue.py` に `ST_CALL = 13` / `ST_DISC = 14` の2ステートを追加し、既存のステートマシンパターンに従って `upd_call` / `upd_disc` / `draw_call_input` / `draw_disc` を実装する。`call_it` はアイテム選択（既存 `draw_isel` 流用）→ テキスト入力（キーボード逐次入力 + ゲームパッド向けプリセット選択）の2段階。`print_disc` は全カテゴリを1画面オーバーレイで表示。メッセージは `assets/messages/en.json` / `ja.json` に追加。

**Tech Stack:** Python 3.10+, Pyxel 2.9.0, 既存 `TextCatalog` / `IdentTable` / `Item`

---

## File Map

| ファイル | 変更内容 |
|---|---|
| `rogue.py` | ST_CALL/ST_DISC 定数、CALL_PRESETS 定数、new_game フィールド追加、upd_play に C/D キートリガー、upd_call/upd_disc/draw_call_input/draw_disc 追加、draw() / update() dispatch 追加 |
| `assets/messages/en.json` | `misc.what_to_call_it`, `misc.discoveries_title`, `misc.nothing_discovered`, `misc.discoveries_hint` を追加 |
| `assets/messages/ja.json` | 同上の日本語版 |
| `tests/test_rogue_baseline.py` | call_it / print_disc のロジックテスト追加 |

---

## Task 1: メッセージ追加

**Files:**
- Modify: `assets/messages/en.json`
- Modify: `assets/messages/ja.json`

- [ ] **Step 1: en.json に4キーを追加**

`assets/messages/en.json` の末尾のオブジェクト閉じ括弧 `}` の直前に追記（既存の最終エントリの後ろにカンマを忘れずに）:

```json
  "misc.what_to_call_it": "What do you want to call it? ",
  "misc.discoveries_title": "Discoveries",
  "misc.nothing_discovered": "(nothing discovered)",
  "misc.discoveries_hint": "[↑↓ scroll / A or Esc to close]"
```

- [ ] **Step 2: ja.json に4キーを追加**

`assets/messages/ja.json` の末尾の `}` 直前に追記:

```json
  "misc.what_to_call_it": "名前をつける：",
  "misc.discoveries_title": "発見リスト",
  "misc.nothing_discovered": "（未発見）",
  "misc.discoveries_hint": "[↑↓スクロール / A または Esc で閉じる]"
```

- [ ] **Step 3: JSON 構文確認**

```bash
python3 -c "import json; json.load(open('assets/messages/en.json')); json.load(open('assets/messages/ja.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add assets/messages/en.json assets/messages/ja.json
git commit -m "feat: add call_it/print_disc message keys to catalogs"
```

---

## Task 2: 定数・フィールド追加

**Files:**
- Modify: `rogue.py` (定数セクション L214–217 付近, `new_game` メソッド L1297 付近)

- [ ] **Step 1: ST_CALL / ST_DISC 定数を追加**

`rogue.py` の L217 (`ST_QUIT = 10; ...`) の次行に追加:

```python
ST_CALL = 13; ST_DISC = 14
```

- [ ] **Step 2: CALL_PRESETS 定数を追加**

定数セクション（`ST_DISC` 追加行の直後）に追加:

```python
CALL_PRESETS = [
    "good", "bad",  "meh",  "skip",
    "try",  "use",  "id?",  "boo",
    "zap",  "hmm",  "ugh",  "yay",
    "wow",  "odd",  "???",  "!!!",
]
```

- [ ] **Step 3: new_game にフィールド追加**

`new_game` メソッド内、`self.cact = None` の行の近く（L1298 付近）に追加:

```python
self.call_input = ""; self.call_preset_idx = 0; self.call_item = None
self.disc_scroll = 0
```

- [ ] **Step 4: 構文チェック**

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add rogue.py
git commit -m "feat: add ST_CALL/ST_DISC constants and CALL_PRESETS"
```

---

## Task 3: テスト追加（TDD）

**Files:**
- Modify: `tests/test_rogue_baseline.py`

- [ ] **Step 1: call_it ロジックテストを追加**

`tests/test_rogue_baseline.py` の末尾に追加:

```python
class TestCallIt(unittest.TestCase):
    def setUp(self):
        from rogue import Game
        self.g = Game.__new__(Game)
        self.g.new_game()

    def test_call_sets_guess(self):
        """oi_know=False のアイテムに仮名が設定される"""
        it = self.g.p.inv[0] if self.g.p.inv else None
        # ポーションを探す
        from rogue import CAT_POT
        pots = [i for i in self.g.p.inv if i.cat == CAT_POT]
        if not pots:
            return  # 初期インベントリにポーションがない場合はスキップ
        it = pots[0]
        it.known = False
        self.g._call_it_apply(it, "boo")
        self.assertEqual(self.g.ident.pg[it.kind], "boo")

    def test_call_clears_guess_when_known(self):
        """oi_know=True なら既存 oi_guess をクリアして何もしない"""
        from rogue import CAT_POT
        pots = [i for i in self.g.p.inv if i.cat == CAT_POT]
        if not pots:
            return
        it = pots[0]
        it.known = True
        self.g.ident.pg[it.kind] = "old_name"
        self.g._call_it_apply(it, "new_name")
        self.assertIsNone(self.g.ident.pg[it.kind])

    def test_call_empty_string_clears_guess(self):
        """空文字確定で oi_guess がクリアされる"""
        from rogue import CAT_SCR
        scrs = [i for i in self.g.p.inv if i.cat == CAT_SCR]
        if not scrs:
            return
        it = scrs[0]
        it.known = False
        self.g.ident.sg[it.kind] = "old"
        self.g._call_it_apply(it, "")
        self.assertIsNone(self.g.ident.sg[it.kind])


class TestPrintDisc(unittest.TestCase):
    def setUp(self):
        from rogue import Game
        self.g = Game.__new__(Game)
        self.g.new_game()

    def test_disc_lines_empty_when_nothing_known(self):
        """何も識別していなければ全カテゴリで nothing_discovered が返る"""
        lines = self.g._disc_lines()
        texts = [t for _, t in lines]
        self.assertTrue(any("nothing" in t.lower() or "未発見" in t for t in texts))

    def test_disc_lines_shows_known_potion(self):
        """oi_know=True のポーションが一覧に現れる"""
        from rogue import CAT_POT, Item
        it = Item(CAT_POT, 0, known=False)
        self.g.ident.pk[0] = True
        lines = self.g._disc_lines()
        texts = [t for _, t in lines]
        # 少なくともポーション名が含まれる行がある
        self.assertTrue(any(t and not t.startswith("--") and not t.startswith("(") for t in texts))
```

- [ ] **Step 2: テストを実行して FAIL を確認**

```bash
python3 -m unittest tests.test_rogue_baseline.TestCallIt tests.test_rogue_baseline.TestPrintDisc -v 2>&1 | head -30
```

Expected: `AttributeError: 'Game' object has no attribute '_call_it_apply'` などの FAIL

- [ ] **Step 3: Commit**

```bash
git add tests/test_rogue_baseline.py
git commit -m "test: add failing tests for call_it/_disc_lines"
```

---

## Task 4: `_call_it_apply` と `_disc_lines` の実装

**Files:**
- Modify: `rogue.py` (`set_know` メソッド L2238 付近の後)

- [ ] **Step 1: `_call_it_apply` を実装**

`set_know` メソッドの直後に追加:

```python
def _call_it_apply(self, it, name: str):
    # misc.c:call_it() — oi_know なら oi_guess クリア、それ以外は name をセット（空文字はクリア）
    from rogue import CAT_POT, CAT_SCR, CAT_RING, CAT_STICK
    def _set(arr, idx, val):
        arr[idx] = val if val else None

    known = (
        (it.cat == CAT_POT   and self.ident.pk[it.kind]) or
        (it.cat == CAT_SCR   and self.ident.sk[it.kind]) or
        (it.cat == CAT_RING  and self.ident.rk[it.kind]) or
        (it.cat == CAT_STICK and self.ident.wk[it.kind])
    )
    if known:
        if it.cat == CAT_POT:   self.ident.pg[it.kind] = None
        elif it.cat == CAT_SCR:   self.ident.sg[it.kind] = None
        elif it.cat == CAT_RING:  self.ident.rg[it.kind] = None
        elif it.cat == CAT_STICK: self.ident.wg[it.kind] = None
        return
    val = name.strip() if name else None
    if it.cat == CAT_POT:   self.ident.pg[it.kind] = val
    elif it.cat == CAT_SCR:   self.ident.sg[it.kind] = val
    elif it.cat == CAT_RING:  self.ident.rg[it.kind] = val
    elif it.cat == CAT_STICK: self.ident.wg[it.kind] = val
```

- [ ] **Step 2: `_disc_lines` を実装**

`_call_it_apply` の直後に追加:

```python
def _disc_lines(self):
    """発見済みアイテム名を (color, text) のリストで返す。things.c:print_disc(*) 相当。"""
    from rogue import CAT_POT, CAT_SCR, CAT_RING, CAT_STICK, Item, POTIONS, SCROLLS, RINGS, STICKS
    nothing = TextCatalog.msg(self.lang, "misc.nothing_discovered")
    result = []

    def section(label, cat, table, known_arr, guess_arr):
        result.append((27, f"-- {label} --"))
        found = 0
        for i, spec in enumerate(table):
            if known_arr[i] or (guess_arr[i] is not None):
                dummy = Item(cat, i, known=known_arr[i])
                result.append((9, self.ident.name(dummy)))
                found += 1
        if found == 0:
            result.append((5, nothing))

    lang = self.lang
    section("Potions" if lang == "en" else "水薬",   CAT_POT,   POTIONS, self.ident.pk, self.ident.pg)
    result.append((0, ""))
    section("Scrolls" if lang == "en" else "巻き物", CAT_SCR,   SCROLLS, self.ident.sk, self.ident.sg)
    result.append((0, ""))
    section("Rings"   if lang == "en" else "指輪",   CAT_RING,  RINGS,   self.ident.rk, self.ident.rg)
    result.append((0, ""))
    section("Sticks"  if lang == "en" else "杖",     CAT_STICK, STICKS,  self.ident.wk, self.ident.wg)
    return result
```

- [ ] **Step 3: テスト実行（PASS 確認）**

```bash
python3 -m unittest tests.test_rogue_baseline.TestCallIt tests.test_rogue_baseline.TestPrintDisc -v 2>&1 | tail -15
```

Expected: `OK` (全テスト PASS)

- [ ] **Step 4: 全テスト確認**

```bash
python3 -m unittest 2>&1 | tail -5
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add rogue.py
git commit -m "feat: implement _call_it_apply and _disc_lines (misc.c/things.c logic)"
```

---

## Task 5: ST_CALL ステート — 入力処理

**Files:**
- Modify: `rogue.py` (`rogue_command_action` L3562 付近, `upd_play` L3625 付近, `upd_item` L3699 付近)

- [ ] **Step 1: `rogue_command_action` に C キー追加**

`rogue_command_action` メソッド内、`return None` の直前に追加:

```python
if self.key_lower(pyxel.KEY_C): return "Call"
```

- [ ] **Step 2: `start_item_action` の "Call" フィルタを追加**

`start_item_action` メソッド内の `if aname=="Throw":` ブロックの前、フィルタ分岐部分（`self.fitems=[i for i in p.inv if ...]`）に "Call" の分岐を追加。

現在 L3261–3269 付近のフィルタブロックは以下のような構造:

```python
self.action_origin = self.st
self.cact = aname; p = self.p
if aname == "Take off":
    self.fitems = [...]
elif aname == "Drop":
    self.fitems = list(p.inv)
...
```

この末尾 `else` / `self.fitems=list(p.inv)` の前に追加:

```python
elif aname == "Call":
    self.fitems = [i for i in p.inv if i.cat in (CAT_POT, CAT_SCR, CAT_RING, CAT_STICK)]
```

- [ ] **Step 3: `start_item_action` の遷移先を ST_CALL に変更**

`start_item_action` 末尾の `self.st=ST_ITEM` に至る直前、`aname=="Throw"` 分岐の else 相当部分:

```python
if aname == "Throw":
    ...
else:
    self.st = ST_ITEM
```

を:

```python
if aname == "Throw":
    ...
elif aname == "Call":
    self.st = ST_CALL
else:
    self.st = ST_ITEM
```

に変更。

- [ ] **Step 4: `upd_call` メソッドを追加**

`upd_item` メソッドの直後に追加:

```python
def upd_call(self):
    # Phase 1: アイテム選択（fitems が空でなく、call_item が None）
    if self.call_item is None:
        dy = self.menu_vertical_press()
        if dy and self.fitems:
            self.icur = (self.icur + dy) % len(self.fitems)
            return
        if self.btn_a():
            it = self.fitems[self.icur] if self.fitems else None
            if it is None:
                self.close_menu(); return
            self.call_item = it
            self.call_preset_idx = 0
            self.call_input = CALL_PRESETS[0]
            return
        if self.btn_overlay_cancel():
            self.close_menu(); return
        return

    # Phase 2: テキスト入力
    dy = self.menu_vertical_press()
    if dy:
        self.call_preset_idx = (self.call_preset_idx - dy) % len(CALL_PRESETS)
        self.call_input = CALL_PRESETS[self.call_preset_idx]
        return
    # キーボード文字入力（Shift なし）
    for key, ch in _KEY_CHAR_MAP:
        if pyxel.btnp(key):
            if self.shift_held() and ch.isalpha():
                self.call_input = (self.call_input + ch.upper())[:16]
            else:
                self.call_input = (self.call_input + ch)[:16]
            return
    if pyxel.btnp(pyxel.KEY_BACKSPACE):
        self.call_input = self.call_input[:-1]
        return
    if self.btn_a() or pyxel.btnp(pyxel.KEY_RETURN):
        self._call_it_apply(self.call_item, self.call_input)
        self.call_item = None; self.call_input = ""; self.call_preset_idx = 0
        self.close_menu()
        # ターン消費なし（misc.c:call_it() 準拠）
        return
    if self.btn_overlay_cancel():
        self.call_item = None; self.call_input = ""; self.call_preset_idx = 0
        self.close_menu(); return
```

- [ ] **Step 5: `_KEY_CHAR_MAP` 定数を追加**

定数セクション（`CALL_PRESETS` の直後）に追加:

```python
_KEY_CHAR_MAP = (
    (pyxel.KEY_A,"a"),(pyxel.KEY_B,"b"),(pyxel.KEY_C,"c"),(pyxel.KEY_D,"d"),
    (pyxel.KEY_E,"e"),(pyxel.KEY_F,"f"),(pyxel.KEY_G,"g"),(pyxel.KEY_H,"h"),
    (pyxel.KEY_I,"i"),(pyxel.KEY_J,"j"),(pyxel.KEY_K,"k"),(pyxel.KEY_L,"l"),
    (pyxel.KEY_M,"m"),(pyxel.KEY_N,"n"),(pyxel.KEY_O,"o"),(pyxel.KEY_P,"p"),
    (pyxel.KEY_Q,"q"),(pyxel.KEY_R,"r"),(pyxel.KEY_S,"s"),(pyxel.KEY_T,"t"),
    (pyxel.KEY_U,"u"),(pyxel.KEY_V,"v"),(pyxel.KEY_W,"w"),(pyxel.KEY_X,"x"),
    (pyxel.KEY_Y,"y"),(pyxel.KEY_Z,"z"),(pyxel.KEY_SPACE," "),
)
```

- [ ] **Step 6: `update()` の dispatch に ST_CALL を追加**

`update()` メソッド内の dispatch ブロック（L3613–3617 付近）:

```python
if self.st==ST_PLAY:   self.upd_play()
elif self.st==ST_MENU: self.upd_menu()
elif self.st==ST_ITEM: self.upd_item()
elif self.st==ST_DIR:  self.upd_dir()
elif self.st==ST_AUX:  self.upd_aux()
```

に追加:

```python
elif self.st==ST_CALL: self.upd_call()
```

- [ ] **Step 7: `upd_play` に D キートリガーを追加**

`upd_play` メソッド内の Rogue コマンド処理（`aname = self.rogue_command_action()` の前）に追加:

```python
if pyxel.btnp(pyxel.KEY_D) and not self.shift_held():
    self.disc_scroll = 0; self.st = ST_DISC; return
```

- [ ] **Step 8: 構文チェック**

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 9: Commit**

```bash
git add rogue.py
git commit -m "feat: ST_CALL state — upd_call with item select + text input"
```

---

## Task 6: ST_DISC ステート — 入力処理

**Files:**
- Modify: `rogue.py`

- [ ] **Step 1: `upd_disc` メソッドを追加**

`upd_call` の直後に追加:

```python
def upd_disc(self):
    lines = self._disc_lines()
    visible = 18  # 表示可能行数
    max_scroll = max(0, len(lines) - visible)
    dy = self.menu_vertical_press()
    if dy:
        self.disc_scroll = max(0, min(self.disc_scroll + dy, max_scroll))
        return
    if self.btn_a() or self.btn_overlay_cancel():
        self.st = ST_PLAY; return
```

- [ ] **Step 2: `update()` dispatch に ST_DISC を追加**

ST_CALL の追加行の直後:

```python
elif self.st==ST_DISC: self.upd_disc()
```

- [ ] **Step 3: 構文チェック**

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add rogue.py
git commit -m "feat: ST_DISC state — upd_disc with scroll and dismiss"
```

---

## Task 7: draw_call_input の実装

**Files:**
- Modify: `rogue.py` (`draw_isel` L3937 付近の後)

- [ ] **Step 1: `draw_call_input` メソッドを追加**

`draw_isel` の直後に追加:

```python
def draw_call_input(self):
    # Phase 1: アイテム選択
    if self.call_item is None:
        self.draw_isel()
        return
    # Phase 2: テキスト入力
    prompt = TextCatalog.msg(self.lang, "misc.what_to_call_it")
    bx, by = ZV_X + 20, ZV_Y + 60; bw = 240; bh = 36
    self._box(bx, by, bw, bh, f"-- {self.cact} --")
    self.txt(bx + 4, by + 14, f"{prompt}", 9)
    cursor = "_" if (pyxel.frame_count // 15) % 2 == 0 else " "
    self.txt(bx + 4, by + 24, f"> {self.call_input}{cursor}", 27)
```

- [ ] **Step 2: `draw()` dispatch に ST_CALL を追加**

`draw()` メソッド内の dispatch ブロック（`elif self.st==ST_ITEM: self.draw_isel()` の後）に追加:

```python
elif self.st==ST_CALL: self.draw_call_input()
```

- [ ] **Step 3: 構文チェック**

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add rogue.py
git commit -m "feat: draw_call_input — item select reuse + text input box with cursor"
```

---

## Task 8: draw_disc の実装

**Files:**
- Modify: `rogue.py`

- [ ] **Step 1: `draw_disc` メソッドを追加**

`draw_call_input` の直後に追加:

```python
def draw_disc(self):
    bx, by = 20, 12; bw = SCR_W - 40; bh = SCR_H - 80
    title = TextCatalog.msg(self.lang, "misc.discoveries_title")
    hint  = TextCatalog.msg(self.lang, "misc.discoveries_hint")
    self._box(bx, by, bw, bh, f"=== {title} ===")
    lines = self._disc_lines()
    visible = (bh - 20) // 9
    start = self.disc_scroll
    for i, (col, text) in enumerate(lines[start:start + visible]):
        if not text:
            continue
        self.txt(bx + 6, by + 16 + i * 9, text[:60], col if col else 9)
    self.txt(bx + 4, by + bh - 10, hint, 5)
```

- [ ] **Step 2: `draw()` dispatch に ST_DISC を追加**

ST_CALL の行の直後:

```python
elif self.st==ST_DISC: self.draw_disc()
```

- [ ] **Step 3: 構文チェック**

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: 全テスト実行**

```bash
python3 -m unittest 2>&1 | tail -5
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add rogue.py
git commit -m "feat: draw_disc — discoveries overlay with scroll (print_disc equivalent)"
```

---

## Task 9: close_menu のリセット処理確認

**Files:**
- Modify: `rogue.py` (`close_menu` L3249 付近)

- [ ] **Step 1: close_menu に call_item リセットを追加**

`close_menu` メソッド（`self.st=ST_PLAY; self.mcur=self.icur=0; ...` の行）に追記:

```python
self.call_item = None; self.call_input = ""; self.call_preset_idx = 0
```

これにより、どこから close_menu を呼んでも ST_CALL 関連フィールドがリセットされる。

- [ ] **Step 2: 構文チェック**

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: 全テスト実行**

```bash
python3 -m unittest 2>&1 | tail -5
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add rogue.py
git commit -m "feat: reset call_item/call_input in close_menu for ST_CALL safety"
```

---

## Task 10: 動作確認・仕上げ

**Files:**
- Modify: `rogue.py` (UI_BUILD スタンプ)

- [ ] **Step 1: ゲーム起動して C キー動作確認**

```bash
pyxel run rogue.py
```

確認項目:
- `C` キー押下でアイテム選択オーバーレイが開く
- ポーション/巻物/指輪/杖のみ表示される（weapon/armor/food は表示されない）
- アイテム選択後、テキスト入力ボックスが表示される
- ↑↓でプリセット名が切り替わる
- キーボード文字を打つとプリセットが上書きされ入力が追記される
- Backspace で1文字削除できる
- Enter/A で確定し、インベントリ表示が更新される（`?`) ポーションが `red potion called boo` など）
- Esc/B でキャンセルされ、ST_PLAY に戻る

- [ ] **Step 2: D キー動作確認**

- `D` キー押下で発見リストオーバーレイが開く
- 何も識別していない状態では各カテゴリに `(nothing discovered)` が表示される
- ポーションを飲んで識別後、再度 `D` で名前が表示される
- ↑↓でスクロールできる
- A/Esc で閉じる

- [ ] **Step 3: 日本語モードで確認**

```bash
PYXEL_ROGUE_LANG=ja pyxel run rogue.py
```

- `C` / `D` 両方のメッセージが日本語で表示されること

- [ ] **Step 4: UI_BUILD スタンプ更新**

`rogue.py` 内の `UI_BUILD` 定数（`"260424_HHMM"` 形式）を現在日時に更新:

```python
UI_BUILD = "260424_HHMM"  # HHMM を実際の時刻に
```

- [ ] **Step 5: 最終テスト**

```bash
python3 -m unittest 2>&1 | tail -5
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add rogue.py
git commit -m "feat: call_it (C key) + print_disc (D key) — misc.c/things.c port complete"
```

---

## Self-Review

### Spec Coverage

| 仕様 | タスク |
|---|---|
| ST_CALL / ST_DISC 定数追加 | Task 2 |
| CALL_PRESETS 定数 | Task 2 |
| `_call_it_apply` ロジック（oi_know 時クリア、空文字クリア） | Task 4 |
| `_disc_lines` ロジック（全カテゴリ、oi_know/oi_guess フィルタ） | Task 4 |
| C キートリガー → ST_CALL | Task 5 |
| D キートリガー → ST_DISC | Task 5 |
| ゲームパッド ↑↓ プリセット選択 | Task 5 |
| キーボード逐次文字入力（最大16文字） | Task 5 |
| Backspace 削除 | Task 5 |
| ターン消費なし | Task 5（close_menu のみ、end_turn 呼ばない） |
| `draw_call_input` | Task 7 |
| `draw_disc` スクロール | Task 8 |
| メッセージ catalog 追加 | Task 1 |
| TDD テスト | Task 3 |

### 確認済み問題なし

- `_KEY_CHAR_MAP` は定数セクションで定義し、`upd_call` より先に参照される（定数は Game クラス外）
- `close_menu` リセットにより ST_CALL 途中からの強制終了でも状態が壊れない
- `_disc_lines` の `Item(cat, i, known=known_arr[i])` は known フラグを正しく渡している
