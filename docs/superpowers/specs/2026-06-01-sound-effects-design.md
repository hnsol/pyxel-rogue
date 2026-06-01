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
4-33  SFX from SE pack, using upstream slot numbers directly
40-43 Dungeon/result BGM
```

Load `assets/rpg-sepack.pyxres` before title BGM setup. The upstream resource says "SE は 04 から入っています", so keep those sound slot numbers unchanged. Rebuild title BGM slots `0..3` after loading, and write dungeon/result BGM to `40..43` so it does not overwrite SE04-33.

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
3. Trap / teleport / explosion / elemental bolt
4. Hit / throw hit
5. Stairs / pickup / potion / scroll / wand generic
6. Miss / UI confirm / error
7. UI cursor

Examples:

- Level-up kill plays level-up over the normal hit sound.
- Healing potion plays heal, not generic potion.
- Lightning wand plays electric, not generic wand.
- Teleport trap plays teleport, not trap.

If later we want layered SFX, add a second SE channel after verifying BGM quality. Initial scope stays one SFX channel.

## SFX Slot Map

| Constant | Slot | SE Pack # | Event |
|----------|------|-----------|-------|
| `SFX_SELECT_LOW` | 4 | SE04 | Menu cursor move |
| `SFX_SELECT_HIGH` | 5 | SE05 | Menu confirm |
| `SFX_PICKUP` | 6 | SE06 | Item / gold pickup |
| `SFX_ERROR` | 7 | SE07 | Invalid action / cursed item / light bad yellow warning |
| `SFX_STAIRS` | 8 | SE08 | Stairs |
| `SFX_WARP` | 10 | SE10 | Teleport |
| `SFX_TRAP` | 12 | SE12 | Trap |
| `HIT_SFX[0]` | 14 | SE14 | Hit variation |
| `SFX_HIT_2` | 15 | SE15 | Unused hit variation |
| `HIT_SFX[1]` | 16 | SE16 | Hit variation |
| `HIT_SFX[2]` | 17 | SE17 | Hit variation |
| `SFX_DEATH` | 18 | SE18 | Death hit, played 3 times with fading volume |
| `SFX_THROW` | 19 | SE19 | Throw |
| `SFX_WAND_ZAP` | 19 | SE19 | Wand/staff generic |
| `SFX_THROW_HIT` | 20 | SE20 | Thrown item hits |
| `SFX_EXPLODE` | 21 | SE21 | Explosion |
| `SFX_ESCAPE` | 23 | SE23 | Escape / phase |
| `SFX_BREATH` | 24 | SE24 | Breath |
| `SFX_ELECTRIC` | 26 | SE26 | Lightning |
| `SFX_ICE` | 27 | SE27 | Cold |
| `SFX_SPELL_USE` | 28 | SE28 | Potion / scroll generic |
| `SFX_SECRET_DOOR` | 32 | SE32 | Secret door found |
| `SFX_HEAL_SMALL` | 32 | SE32 | Healing |
| `SFX_HEAL_LARGE` | 33 | SE33 | Level up |
| `SFX_DEATH_ECHO_1` | 34 | SE18 copy | Death echo, about 65% volume |
| `SFX_DEATH_ECHO_2` | 35 | SE18 copy | Death echo, about 35% volume |
| `SFX_HIT_MISS` | 36 | custom | Attack / throw miss, short "churun" phrase |
| `SFX_ALARM` | 37 | SE13 first 24 steps | Heavy bad yellow warning |

## Integration Scope

Initial call sites:

| Area | Event | SFX |
|------|-------|-----|
| Combat | player or monster hit | random `HIT_SFX` = SE14, SE16, SE17 |
| Combat | player or monster miss | `SFX_HIT_MISS` = short "churun" phrase |
| Combat | monster killed / level up | normal hit / `SFX_HEAL_LARGE` |
| Combat | throw / thrown hit / thrown miss | `SFX_THROW` / `SFX_THROW_HIT` / `SFX_HIT_MISS` |
| Result | death | `DEATH_SFX_SEQUENCE` = SE18 + 65% echo + 35% echo |
| Exploration | stairs | `SFX_STAIRS` |
| Exploration | secret door found | `SFX_SECRET_DOOR` = SE32 |
| Exploration | harmful trap / teleport | `SFX_ALARM` / `SFX_WARP` |
| Status | hunger warning | `SFX_ERROR` |
| Status | strength loss / poison / armor weaken | `SFX_ALARM` |
| Exploration | pickup | `SFX_PICKUP` = SE06 |
| Items | potion / scroll | `SFX_SPELL_USE` |
| Items | healing potion | `SFX_HEAL_SMALL` |
| Items | wand generic / electric / cold | `SFX_WAND_ZAP` / `SFX_ELECTRIC` / `SFX_ICE` |
| UI | cursor / confirm / invalid | `SFX_SELECT_LOW` / `SFX_SELECT_HIGH` / `SFX_ERROR` |

Use `request()` at call sites, not direct `pyxel.play()`. Stairs are the one exception: use the SFX controller's immediate playback path, stop dungeon BGM first, then continue the floor transition so `08:階段` is not masked by the BGM handoff.

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

- combat hit, miss, monster hit, throw, thrown hit/miss, kill, level up
- stairs, trap, teleport, pickup
- potion, healing potion, scroll, wand, electric/cold wand
- UI cursor, confirm, invalid/cursed action
- BGM ch3 returns after SFX and no SFX is cut off by floor/BGM updates
