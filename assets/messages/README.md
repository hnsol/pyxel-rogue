# Rogue 5.4.4 Message Catalogs

This directory contains extracted message catalogs for the Pyxel Rogue i18n
work.

## Files

- `en.json`: English message templates extracted from Rogue 5.4.4 C sources.
- `ja.json`: Japanese templates matched from Rogue2.Official `mesg_J` where the
  English source line could be matched confidently.
- `manifest.json`: source locations, placeholder lists, extraction origin, and
  Japanese match status for every English key.

## Key Rules

Rogue 5.4.4 source keys use this shape:

```text
<source_file_basename>.<snake_case_summary>
```

Examples:

```text
fight.you_hit_target
command.no_monster_there
pack.you_now_have_item_item2
```

When two messages in the same source normalize to the same summary, a numeric
suffix is appended.

Pyxel Rogue-specific runtime messages use these namespaces:

- `pyxel.*`: current Pyxel-side logs and portable UI messages.
- `menu.*`: menu labels used through `TextCatalog.menu()`.
- `trap.*`: trap names used through `TextCatalog.trap()`.

## Placeholder Vocabulary

The extraction keeps C `printf` placeholders out of runtime message values and
uses Python `str.format` style placeholders instead.

Current placeholders:

```text
action, armor, cause, color, color2, command, command2, command3, command4,
count, count2, damage, depth, exp, exp_level, file, gold, hp, hp_width, item,
item2, level, max_hp, max_hp_width, max_strength, monster, name, palette,
strength, subject, target, trap, turn, user, value, value2, version, x, y
```

Prefer the existing names when adding keys. Add a new placeholder only when the
value cannot be expressed clearly with the existing vocabulary, and record it in
`manifest.json`.

## Extraction Notes

The English catalog was generated from direct `msg()` / `addmsg()` format
strings in `vendor/rogue544/*.c`, then supplemented with message-bearing arrays
referenced by those calls:

- `fight.c`: `h_names[]`, `m_names[]`
- `extern.c`: `tr_name[]`
- `io.c`: `state_name[]`
- `potions.c`: `p_actions[]`

Some Rogue 5.4.4 messages are assembled conditionally by repeated `addmsg()`
calls. Those fragments are kept at their original append points so later phases
can preserve the original control flow instead of flattening away terse,
wizard, and branch-specific behavior.

## Japanese Matching

`ja.json` contains keys matched from
`vendor/rogue2_official_messages/mesg_E` and `mesg_J`, plus hand-completed
entries where Rogue 5.4.4 has no direct Rogue2.Official line. Missing Japanese
keys are listed under `__summary__.ja_missing_keys` in `manifest.json` and
should fall back to English until a translation is added.

`ja_status` values:

- `matched`: the Japanese line matched and placeholder counts align.
- `manual`: the Japanese text was completed by hand, typically for message
  fragments, wizard/debug strings, or Rogue 5.4.4-only wording.
- `missing`: no confident Rogue2.Official match was found.

## Adding Messages

1. Add the English template to `en.json` with an alphabetically sorted key.
2. Add a matching `manifest.json` entry with `source`, `params`, `origin`, and
   `ja_status`.
3. Add a `ja.json` value only when there is a confirmed translation.
4. Re-run JSON validation:

```bash
python3 -m json.tool assets/messages/en.json >/tmp/en.checked.json
python3 -m json.tool assets/messages/ja.json >/tmp/ja.checked.json
python3 -m json.tool assets/messages/manifest.json >/tmp/manifest.checked.json
```
