[English | [日本語](README.md)]

# Rogue V5 on Pyxel

Rogue V5 on Pyxel is an ASCII-based roguelike made with Pyxel, aiming to recreate the original Rogue experience.

The goal is for clearing this Pyxel version to mean that you could clear Rogue V5. It keeps the feel of the Rogue V5 line in mind, uses the Rogue 5.4.4 C source as a verifiable base text for game mechanics, and adapts display, input, and portability for Pyxel and Pyxel Web.

## Goal

- Build an ASCII-based Pyxel version of the original Rogue
- Keep the game logic easy to compare with the Rogue 5.4.4 C source
- Make it playable in browsers, on desktop, SteamDeck, and handheld game devices
- Preserve Rogue-like exploration choices and tension instead of adding overly convenient modern UI
- Grow toward English/Japanese switching while referencing the Japanese Rogue tradition

For detailed design notes, see [DESIGN.md](docs/DESIGN.md). For the task list and current progress, see [TODO.md](docs/TODO.md).

## Screenshot

![Rogue V5 on Pyxel screenshot](docs/images/pyxel-rogue-screenshot.png)

Gameplay view with the Rogue 5.4.4-style 80-column ASCII map, 512x320 corner HUD, and proximity message log.

## Play on the Web

You can launch the game in a browser with Pyxel Web Launcher.

[Launch Rogue V5 on Pyxel on the Web](https://kitao.github.io/pyxel/web/launcher/?run=hnsol/pyxel-rogue/master/rogue&gamepad=enabled)

The web version lets you try the game without installing Python or Pyxel locally. The URL enables the virtual gamepad, which is useful for phones and tablets.

For faster device debugging, build a local HTML file. By default this builds the main `rogue` variant:

```bash
tools/build_web.sh
```

The output is `web/index.html`.
To build the Nyandor beta:

```bash
PYXEL_ROGUE_VARIANT=nyandor tools/build_web.sh
```

To check that the tracked web build is current after program changes:

```bash
tools/check_web_build.sh
```

GitHub Pages uses the root of the `gh-pages` branch. This keeps generated files out of the `main` root and `docs/`; publish the generated `web/` output with:

```bash
PYXEL_ROGUE_SCORE_URL="Scoreboard URL" tools/deploy_pages_clean.sh
```

Set `PYXEL_ROGUE_SCORE_URL` to the online scoreboard deployment URL. A single Google Spreadsheet is split by variant tabs such as `scores_nyandor` and `scores_rogue`. Keep URLs out of the repository and pass them only as environment variables when deploying.
The Pages root is built as the `Cat and Amulet of Nyandor` beta, while `/rogue/` is built as the main debug build.

## Download and Play Locally

Python 3.10+ and uv are required.

```bash
git clone https://github.com/hnsol/pyxel-rogue.git
cd pyxel-rogue
uv run --with pyxel pyxel run rogue.py
```

To start with Japanese text:

```bash
PYXEL_ROGUE_LANG=ja uv run --with pyxel pyxel run rogue.py
```

Basic developer checks:

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
python3 tools/check_project_rules.py
uvx ruff check .
python3 -m unittest
PYXEL_ROGUE_LANG=ja python3 -m unittest
```

For Rogue 5.4.4 fidelity work, keep the original C source locally as a reference. This directory is ignored by git and is not included in this repository.

```bash
mkdir -p vendor
git clone https://github.com/Davidslv/rogue.git vendor/rogue544
```

## Controls

Gamepad:

- D-pad: Move in 8 directions
- Hold Start: Diagonal assist
- A: Confirm / pick up / stairs
- B tap: Menu / cancel
- B hold + D-pad: Dash
- A+B: Wait a turn
- Select: Info (Inventory / Log / Settings / Help); press left/right in Info to switch tabs; press Select to close
- Action menu: equipment, items, search, trap inspect, quit
- Title screen: choose `CONTINUE` when a save exists. Choose difficulty after selecting `ENTER DUNGEON`. Changes are saved.
- Scoreboard: left/right changes Local / This Week / Season, up/down changes the difficulty filter.
- Settings: Auto pickup / Language / Palette / Save and quit. Settings and suspend saves are saved.
- Select+A: Quick throw (choose direction, then item)
- Select+B: Search around all 8 neighboring tiles
- Select+D-pad: Inspect a discovered trap

Keyboard:

- Arrow keys / HJKL: Move
- YUBN: Diagonal movement
- Hold Space: Diagonal assist
- Enter: Confirm / pick up / stairs
- Enter+Esc: Wait a turn
- Shift+direction: Dash
- Esc: Menu / cancel
- Tab: Info (Inventory / Log / Settings / Help); press left/right in Info to switch tabs; press Tab to close
- Tab+Enter: Quick throw
- Tab+Esc: Search around all 8 neighboring tiles
- Tab+direction: Inspect a discovered trap
- .: Wait a turn
- ,: Pick up
- > / <: Go down / up stairs
- s: Search around all 8 neighboring tiles
- t: Quick throw
- ^: Trap Inspect (choose direction)
- i: Inventory
- I: Inventory one item
- ?: Help
- /: Identify a symbol
- Ctrl+P: Repeat last message
- Ctrl+R: Redraw
- m: Move onto without picking up
- f/F: Fight / Fight to death
- a: Again (repeat the last command)
- Digits: Count prefix for search / wait / movement / Again
- o: Settings
- v: Version
- ) / ] / = / @: Current weapon / armor / rings / status
- q/r/e/z: Quaff / Read / Eat / Zap
- w/W/T/P/R: Wield / Wear / Take off / Put on / Remove ring
- Q: Quit

Use Zap from the menu to choose a wand or staff, then choose a direction.

## Current Status

Implemented overview:

- Rogue 5.4.4-style 80x24 logical map, 80x22 terrain view, 512x320 fictional retro-console layout, corner HUD with lower-left HP and lower-right status, and proximity message logs that stay readable on handhelds
- 3x3-sector dungeon generation with rooms, passages, and doors
- 26 monster types, combat, hunger, and natural HP recovery
- Potions, scrolls, food, weapons, armor, rings, identification, inventory, and curses
- Wand/staff 14-type table, random materials, charges, directional Zap entry, light, single-target monster effects, and haste/slow monster effects
- Search, traps, hidden doors, hidden passages, and trap inspection
- Amulet of Yendor and depth-1 return victory while carrying it
- Auto-pickup toggle and throwing animation
- Tombstone death screen
- Victory score adds sold pack worth following Rogue 5.4.4 `total_winner()`
- Startup logo, first-run language selection, title screen with BGM, default Guest mode, and Online / Guest Mode switching
- One-slot suspend save following the original Rogue style. Saving exits the run, and a successful restore consumes the save.
- Local score saving, Weekly / Season online scoreboard viewing, optional online-ID score sync, and anonymous Guest sync metrics
- Gamepad-oriented A/B/Start/Select + D-pad controls
- JSON message/term catalogs for English/Japanese text switching, plus logic test foundation
- Bundled Rogue2.Official `mesg_E` / `mesg_J` files as wording reference data

See [TODO.md](docs/TODO.md) for the detailed implementation status.

## Roadmap

- Wand/staff bolt, magic missile, and drain life effects
- More Rogue 5.4.4 expectation tests
- HUD / Inventory / Help / Death text catalog coverage
- Responsive layout and font selection
- In-dungeon BGM
- Full score history
- Replay support

## Links

Rogue / Rogue 5.4.4:

- [RogueBasin: Rogue](https://www.roguebasin.com/?title=Rogue)
- [Davidslv/rogue: Original Rogue Game 5.4.4](https://github.com/Davidslv/rogue)

Rogue Clone / Japanese Rogue:

- [RogueBasin: Rogue Clone](https://www.roguebasin.com/index.php/Rogue_Clone)
- [suzukiiichiro/Rogue2.Official](https://github.com/suzukiiichiro/Rogue2.Official)

Pyxel:

- [Pyxel User Guide](https://kitao.github.io/pyxel/web/user-guide/)
- [kitao/pyxel](https://github.com/kitao/pyxel)
- [Pyxel PyPI](https://pypi.org/project/pyxel/)
- [How To Use Pyxel Web](https://github.com/kitao/pyxel/wiki/How-To-Use-Pyxel-Web/3c7ccc624e95584ecc1c9696628cafca91bff7df)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
