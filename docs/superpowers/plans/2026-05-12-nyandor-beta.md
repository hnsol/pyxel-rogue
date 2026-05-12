# Nyandor Beta Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Cat and Amulet of Nyandor 5F beta variant that starts in Normal mode and can be deployed beside the main Rogue build.

**Architecture:** Keep one codebase. Add a small variant layer selected by `PYXEL_ROGUE_VARIANT`, with the default build remaining `rogue`. The Nyandor variant overrides title text, fixed difficulty, 5F objective, cat item placement, drop rules, victory text, and Web output paths.

**Tech Stack:** Python 3, Pyxel, unittest, shell build scripts.

---

### Task 1: Variant Configuration

**Files:**
- Modify: `rogue.py`
- Test: `tests/test_rogue_baseline.py`

- [x] Add `VARIANT_ROGUE`, `VARIANT_NYANDOR`, `GAME_VARIANT`, and helpers for title, fixed difficulty, target depth, and objective item naming.
- [x] Add tests that `PYXEL_ROGUE_VARIANT=nyandor` fixes difficulty to Normal and exposes Nyandor title lines.

### Task 2: Cat Objective

**Files:**
- Modify: `rogue.py`
- Test: `tests/test_rogue_baseline.py`

- [x] Spawn one `CAT_AMULET` item with `variant_item="nyandor_cat"` on depth 5 in Nyandor only.
- [x] Render the item as `c`.
- [x] Name it `The Cat (wearing the Amulet of Nyandor)`.
- [x] On pickup, set `p.has_amulet=True`, occupy one inventory slot, and log dry UNIX-style recovery text.
- [x] Reject Drop for that item without consuming a turn.
- [x] On depth 1 upstairs with the cat, enter victory with Nyandor victory text.

### Task 3: Web Outputs

**Files:**
- Modify: `tools/build_web.sh`
- Modify: `tools/deploy_pages.sh`
- Modify: `README.md`

- [x] Let `tools/build_web.sh` accept `PYXEL_ROGUE_WEB_OUT_DIR`.
- [x] Let deploy build Nyandor at Pages root and Rogue at `rogue/`.
- [x] Document root Nyandor and `/rogue/` debug build.

### Task 4: Verification

**Files:**
- Modify: `NOTES.md` only if UI notes are processed.

- [x] Run `python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"`.
- [x] Run `python3 -m unittest`.
- [x] Run `PYXEL_ROGUE_LANG=ja python3 -m unittest`.
- [x] Run `tools/build_web.sh` for the default build if Pyxel CLI is available.
