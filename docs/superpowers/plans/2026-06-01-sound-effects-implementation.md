# Sound Effects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add prioritized sound effects for visible gameplay and UI events without changing Rogue 5.4.4 game state.

**Architecture:** `pyxel_rogue/rogue_sfx.py` owns SFX slots, asset loading, priority arbitration, and ch3 playback. `DungeonBgmController` cooperates by leaving ch3 alone while SFX is active and resuming current ch3 BGM afterward. `rogue.py` loads assets, wires controllers, and requests SFX at event boundaries.

**Tech Stack:** Python 3.10, Pyxel, unittest, existing Pyxel mock tests.

---

### Task 1: SFX Controller

**Files:**
- Create: `pyxel_rogue/rogue_sfx.py`
- Create: `tests/test_rogue_sfx.py`

- [x] Write failing unittest coverage for priority arbitration, playback on ch3, BGM resume after completion, missing asset disabling, and upstream sound numbering.
- [x] Run `python3 -m unittest tests.test_rogue_sfx` and confirm expected failures.
- [x] Implement `SfxController`, constants, priority table, `copy_sound()`, and `load_se_pack()`.
- [x] Run `python3 -m unittest tests.test_rogue_sfx` and confirm pass.

### Task 2: BGM/SFX Channel Cooperation

**Files:**
- Modify: `pyxel_rogue/rogue_bgm.py`
- Modify: `tests/test_rogue_baseline.py`

- [x] Write failing unittest coverage for SFX-active ch3 exclusion and ch3 resume after a key change.
- [x] Run focused unittest and confirm expected failure.
- [x] Add an optional `sfx_active` callback to `DungeonBgmController`, skip ch3 stop/play while active, and add `resume_ch()`.
- [x] Run focused unittest and confirm pass.

### Task 3: Game Wiring

**Files:**
- Modify: `rogue.py`
- Modify: `tests/test_rogue_baseline.py`

- [x] Write failing unittest coverage that `Game` creates SFX, wires it to dungeon BGM, and calls `sfx.update()` each frame.
- [x] Implement load/init/update wiring.
- [x] Run focused unittest and confirm pass.

### Task 4: Event Call Sites

**Files:**
- Modify: `rogue.py`
- Modify: `tests/test_rogue_sfx.py`

- [x] Add tests or static checks that gameplay/UI call sites use `sfx.request()`.
- [x] Add requests for combat, stairs, traps, teleport, pickup, potion, scroll, wand, UI cursor, confirm, and invalid/cursed actions.
- [x] Run focused tests and confirm pass.

### Task 5: Assets, Docs, Verification

**Files:**
- Create: `assets/rpg-sepack.pyxres`
- Create: `assets/THIRD_PARTY.md`
- Modify: `docs/design/bgm.md`

- [x] Download the SE pack asset.
- [x] Record source and use terms in `assets/THIRD_PARTY.md`.
- [x] Run `python3 -m unittest`, `PYXEL_ROGUE_LANG=ja python3 -m unittest`, `python3 tools/check_project_rules.py`, and `uvx ruff check .`.
