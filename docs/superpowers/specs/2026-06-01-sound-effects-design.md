# Sound Effects Design

## Context

Pyxel Rogue has BGM but no sound effects. Add SFX for player-visible events without changing Rogue 5.4.4 game state. SFX is presentation only.

Use `shiromofufactory/pyxel-rpg-sepack` as the first SE source. The upstream README permits use as-is or modified, with no usage restriction and no required author report. Record this in a repo-local third-party asset note when the asset is added.

## Architecture

New files:

- `pyxel_rogue/rogue_sfx.py` — SFX constants, priority table, `SfxController`
- `assets/rpg-sepack.pyxres` — SE resource file
- `assets/THIRD_PARTY.md` — source URL and use terms for bundled third-party assets

Modified files:

- `pyxel_rogue/rogue_bgm.py` — allow temporary ch3 exclusion and ch3 resume
- `rogue.py` — load SE pack, initialize `SfxController`, add event call sites
- `docs/design/bgm.md` — note BGM/SFX channel ownership

## Asset Loading

Sound slots:

```text
0-3   Title BGM
4-7   Dungeon/result BGM
8-37  SFX copied from SE pack slots 4-33
```

Load `assets/rpg-sepack.pyxres` before title BGM setup. After loading, copy slots `4..33` to `8..37`, then rebuild title BGM slots `0..3` and allow dungeon BGM to overwrite `4..7`.

Do not introduce `numpy` as a project dependency. Prefer a Pyxel-native or standard-library copy path. If Pyxel exposes mutable sound sequence fields in the target runtime, copy those directly. If not, expand the `.pyxres` resource as a zip during development and add the needed `soundXX` files to a local resource layout before packaging.

Missing asset behavior: SFX silently disables itself and the game still starts.

## Channel Strategy

SFX uses channel `3`. Dungeon/result BGM normally uses channels `0..3`, but must treat ch3 as unavailable while SFX is active.

`SfxController` owns these responsibilities:

- accept event requests through `request(slot)`
- keep at most one pending sound per frame
- choose the highest-priority pending sound
- play it on ch3
- expose `is_active()`
- call `bgm.resume_ch(3)` once the SFX has finished

`DungeonBgmController` owns these responsibilities:

- when SFX is active, never stop or replay ch3
- when BGM key changes during SFX, update ch0-2 immediately and leave ch3 alone
- after SFX ends, `resume_ch(3)` plays the current BGM slot for ch3 if BGM is active
- `stop()` must stop all BGM channels only when no SFX is active; otherwise it must leave ch3 to the SFX controller

This prevents stairs, teleport, or item-use SFX from being cut off by `update_dungeon_bgm()` in the same frame.

## SFX Arbitration

Multiple events can happen in one command. `request()` queues by priority; `update()` plays only the strongest request for that frame.

Priority order:

1. Player death / result transition
2. Level up / heal
3. Kill / trap / teleport / explosion / elemental bolt
4. Hit / miss / monster hit
5. Stairs / pickup / potion / scroll / wand generic
6. UI confirm / error
7. UI cursor

Examples:

- Level-up kill plays level-up, not kill.
- Healing potion plays heal, not generic potion.
- Lightning wand plays electric, not generic wand.
- Teleport trap plays teleport, not trap.

If later we want layered SFX, add a second SE channel after verifying BGM quality. Initial scope stays one SFX channel.

## SFX Slot Map

| Constant | Slot | SE Pack # | Event |
|----------|------|-----------|-------|
| `SFX_SELECT_LOW` | 8 | SE04 | Menu cursor move |
| `SFX_SELECT_HIGH` | 9 | SE05 | Menu confirm |
| `SFX_ERROR` | 11 | SE07 | Invalid action / cursed item |
| `SFX_STAIRS` | 12 | SE08 | Stairs |
| `SFX_WARP` | 14 | SE10 | Teleport |
| `SFX_TRAP` | 16 | SE12 | Trap |
| `SFX_HIT_PLAYER` | 18 | SE14 | Player hits monster |
| `SFX_HIT_MISS` | 19 | SE15 | Player misses |
| `SFX_HIT_MONSTER` | 20 | SE16 | Monster hits player |
| `SFX_KILL` | 22 | SE18 | Monster killed |
| `SFX_WAND_ZAP` | 23 | SE19 | Wand/staff generic |
| `SFX_EXPLODE` | 25 | SE21 | Explosion |
| `SFX_ESCAPE` | 27 | SE23 | Escape / phase |
| `SFX_BREATH` | 28 | SE24 | Breath |
| `SFX_ELECTRIC` | 30 | SE26 | Lightning |
| `SFX_ICE` | 31 | SE27 | Cold |
| `SFX_SPELL_USE` | 32 | SE28 | Potion / scroll generic |
| `SFX_PICKUP` | 34 | SE30 | Item / gold pickup |
| `SFX_HEAL_SMALL` | 36 | SE32 | Healing |
| `SFX_HEAL_LARGE` | 37 | SE33 | Level up |

## Integration Scope

Initial call sites:

| Area | Event | SFX |
|------|-------|-----|
| Combat | player hit / miss | `SFX_HIT_PLAYER` / `SFX_HIT_MISS` |
| Combat | monster hit | `SFX_HIT_MONSTER` |
| Combat | monster killed / level up | `SFX_KILL` / `SFX_HEAL_LARGE` |
| Exploration | stairs | `SFX_STAIRS` |
| Exploration | trap / teleport | `SFX_TRAP` / `SFX_WARP` |
| Exploration | pickup | `SFX_PICKUP` |
| Items | potion / scroll | `SFX_SPELL_USE` |
| Items | healing potion | `SFX_HEAL_SMALL` |
| Items | wand generic / electric / cold | `SFX_WAND_ZAP` / `SFX_ELECTRIC` / `SFX_ICE` |
| UI | cursor / confirm / invalid | `SFX_SELECT_LOW` / `SFX_SELECT_HIGH` / `SFX_ERROR` |

Use `request()` at call sites, not direct `pyxel.play()`.

Do not add SFX to hidden or non-player-visible state changes. For example, monster AI path decisions and background daemon ticks stay silent.

## Tests

Use repo-standard test commands:

```bash
python3 -m unittest
PYXEL_ROGUE_LANG=ja python3 -m unittest
python3 tools/check_project_rules.py
uvx ruff check .
```

Focused tests:

- `SfxController` chooses highest priority among same-frame requests
- `SfxController` plays on ch3 and resumes BGM only after `play_pos(3)` is done
- missing asset disables SFX without failing startup
- dungeon BGM does not stop or replay ch3 while SFX is active
- BGM key change during SFX updates ch0-2 and resumes ch3 to the current key after SFX
- common call sites use `request()` and do not call `pyxel.play()` directly

Manual verification:

- combat hit, miss, monster hit, kill, level up
- stairs, trap, teleport, pickup
- potion, healing potion, scroll, wand, electric/cold wand
- UI cursor, confirm, invalid/cursed action
- BGM ch3 returns after SFX and no SFX is cut off by floor/BGM updates
