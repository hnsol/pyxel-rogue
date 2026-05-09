# Rogue 5.4.4 Term Catalogs

This directory contains item names, monster names, potion colors, and compact
HUD labels used by `TextCatalog`.

Rules:

- `en.json` and `ja.json` must have the same nested keys.
- Runtime fallback exists only for missing assets or unexpected keys.
- Japanese gameplay should not depend on English fallback during normal tests.
