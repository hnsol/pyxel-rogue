# Combat Messages Diff

## Rogue 5.4.4 references

- `vendor/rogue544/fight.c: fight()`
- `vendor/rogue544/fight.c: attack()`
- `vendor/rogue544/fight.c: hit()`
- `vendor/rogue544/fight.c: miss()`
- `vendor/rogue544/fight.c: thunk()`
- `vendor/rogue544/fight.c: bounce()`
- `vendor/rogue544/fight.c: killed()`
- `vendor/rogue544/fight.c: h_names[]`
- `vendor/rogue544/fight.c: m_names[]`

## Pyxel Rogue mapping

- `Game.p_attack()` maps player melee to `hit(NULL, mname, terse)` and `miss(NULL, mname, terse)` message families.
- `Game.m_attack()` maps monster melee to `hit(mname, NULL, FALSE)` and `miss(mname, NULL, FALSE)` message families.
- `Game.throw()` maps thrown attacks to `thunk()` and `bounce()`.
- `Game.award_monster_kill()` keeps experience and level-up side effects only.

## Previous problem

Combat logs used fixed Pyxel messages:

- `you hit the {monster}` / `you miss the {monster}`
- `the {monster} hit you` / `the {monster} misses`
- `You defeated the {monster}. ({exp} exp)`
- thrown hit logged `({damage})`

Rogue 5.4.4 uses four hit and four miss variants per attacker side, and `killed()` does not print an experience amount.

## New behavior

- Player melee hit/miss selects from the four `h_names[]` / `m_names[]` player-side variants.
- Monster melee hit/miss selects from the four monster-side variants.
- Kill logs use `Defeated {target}` and no longer include `(3 exp)` style text.
- Experience gain and level-up handling remain unchanged in `award_monster_kill()`.
- Weapon throws use `the {item} hits {target}` / `the {item} misses {target}`.
- Non-weapon throws use `you hit {target}` / `you missed {target}`.
- Throw hit logs no longer include damage numbers.

## Known differences

Rogue 5.4.4 can build one pending message with `addmsg()` and append `.  Defeated {mname}` through `has_hit`. Pyxel Rogue stores completed strings in `self.msgs` and renders them as separate log rows. To avoid adding an `addmsg()/endmsg()` buffering layer just for this phase, a killing hit is logged as two rows: the hit variant, then `Defeated {target}`.

English monster names use `the {monster}` for targets and `The {monster}` for monster attack subjects. Japanese names do not add an article.
