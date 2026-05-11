# Difficulty Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Easy / Normal / Classic / Strict difficulty with cleaned-up identification state, integrated identify scroll for Normal/Easy, Strict HUD restrictions, and difficulty-separated scoreboards.

**Architecture:** Put difficulty data in a small profile module, keep Rogue 5.4.4 mechanics as the base, and make Rogue 5.4.5p `idscrl` an explicit profile rule. Split identification operations into type knowledge, instance knowledge, and call/guess so difficulty rules do not leak item details.

**Tech Stack:** Python 3.10+, Pyxel 2.9.0, `unittest`, existing single-file `rogue.py` plus small helper modules.

---

### Task 1: Add Difficulty Profiles

**Files:**
- Create: `rogue_difficulty.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests for difficulty IDs, labels, defaults, score multipliers, `idscrl`, Easy type-known behavior, and Strict HUD behavior.
- [ ] Create `rogue_difficulty.py` with:
  - `DIFF_EASY = "easy"`
  - `DIFF_NORMAL = "normal"`
  - `DIFF_CLASSIC = "classic"`
  - `DIFF_STRICT = "strict"`
  - default `DIFF_NORMAL`
  - `score_multiplier = 1.0` for all profiles
  - `scoreboard_key` per difficulty
  - `easy_type_known`
  - `idscrl`
  - `show_status_hud`
- [ ] Run targeted tests and confirm they pass.

### Task 2: Add Difficulty to Settings

**Files:**
- Modify: `rogue_lang.py`
- Modify: `rogue.py`
- Modify: `assets/messages/en.json`
- Modify: `assets/messages/ja.json`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests that `Settings(difficulty="bad")` normalizes to Normal and save/load round-trips difficulty.
- [ ] Extend settings serialization with `difficulty`.
- [ ] Add Settings row `Difficulty`.
- [ ] Add value cycling order: Easy -> Normal -> Classic -> Strict -> Easy.
- [ ] Add localized labels.
- [ ] Run settings tests.

### Task 3: Refactor Identification State APIs

**Files:**
- Modify: `rogue.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests for:
  - type knowledge only does not reveal weapon/armor/ring/stick instance details
  - instance knowledge only reveals instance details where relevant
  - call guesses remain separate
  - `set_know()` still matches Rogue 5.4.4 `wizard.c:set_know()`
- [ ] Add methods:
  - `type_known(it)`
  - `set_type_known(it, known=True)`
  - `set_instance_known(it, known=True)`
  - `clear_type_guess(it)`
  - `set_know(it)` as compatibility wrapper
- [ ] Change existing direct `ident.pk/sk/rk/wk` checks where a helper improves clarity, without broad churn.
- [ ] Run identify/call/discovery tests.

### Task 4: Apply Easy Initial Knowledge

**Files:**
- Modify: `rogue.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests that Easy starts potion/scroll/ring/stick types known and `D` shows those discoveries.
- [ ] Add failing tests that Easy still hides ring bonus and stick charges until `Item.known`.
- [ ] In `new_game()`, after `IdentTable` creation, apply Easy type knowledge.
- [ ] Run Easy-related tests.

### Task 5: Add `idscrl` Scroll Table

**Files:**
- Modify: `rogue.py`
- Modify: `rogue_scrolls.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests for Rogue 5.4.5p `extern.c:scr_info2[]`:
  - index 5 name `identify`
  - index 5 prob `27`, worth `100`
  - old identify indexes 6-9 prob `0`, worth `0`
- [ ] Add helper to produce active scroll table from difficulty.
- [ ] Keep Classic/Strict using Rogue 5.4.4 `extern.c:scr_info[]`.
- [ ] Ensure item generation uses active scroll probabilities.
- [ ] Run scroll table tests.

### Task 6: Integrate Identify Scroll Behavior

**Files:**
- Modify: `rogue.py`
- Modify: `rogue_scrolls.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests:
  - Normal `identify` can target any item needing identification
  - Classic identify potion only targets potions
  - Strict identify remains Classic-style
  - consumed-before-selection behavior remains unchanged
  - no-target behavior still consumes one scroll and reports unease
- [ ] Update `identify_scroll_target_cats()` to return all identifiable categories for `idscrl`.
- [ ] Update read-scroll message to support `identify`.
- [ ] Keep `set_know()` as the final selected-item effect.
- [ ] Run identify scroll tests.

### Task 7: Strict HUD Status Filtering

**Files:**
- Modify: `rogue.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests that Strict hides HUD status-condition labels.
- [ ] Ensure gameplay state and logs are unchanged.
- [ ] Gate only the helpful HUD status rendering with `show_status_hud`.
- [ ] Run HUD tests.

### Task 8: Difficulty-Separated Scores

**Files:**
- Modify: `rogue_scores.py`
- Modify: `rogue.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Add failing tests:
  - score entry includes `difficulty`
  - `score_entry_id()` includes difficulty
  - local top scores filter by difficulty
  - period/online score helpers preserve and filter difficulty
  - score value itself is not multiplied
- [ ] Add optional `difficulty` argument to score filtering helpers.
- [ ] Save current game difficulty in result entries.
- [ ] Display current scoreboard difficulty.
- [ ] Run score tests.

### Task 9: Docs and Build Stamp

**Files:**
- Modify: `DESIGN.md`
- Modify: `TODO.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `rogue.py`
- Modify: `tests/test_rogue_baseline.py`

- [ ] Record 5.4.4 vs 5.4.5p `idscrl` difference in `DESIGN.md`.
- [ ] Record scoreboard split and no multiplier policy.
- [ ] Mark relevant TODO items complete.
- [ ] Document Settings difficulty.
- [ ] Update `UI_BUILD`.
- [ ] Run docs/build-stamp tests.

### Task 10: Full Verification

**Files:**
- Test only.

- [ ] Run `python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"` and expect `OK`.
- [ ] Run `python3 -m unittest` and expect all tests pass.
- [ ] Run `PYXEL_ROGUE_LANG=ja python3 -m unittest` and expect all tests pass.
- [ ] Confirm `git diff` contains no implementation outside the approved scope.
