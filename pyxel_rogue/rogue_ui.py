from pyxel_rogue.rogue_items import CAT_ARM, CAT_FOOD, CAT_POT, CAT_RING, CAT_SCR, CAT_STICK, CAT_WPN

ST_PLAY = 0
ST_MENU = 1
ST_ITEM = 2
ST_DIR = 3
ST_DEAD = 4
ST_INVENTORY = 5
ST_HELP = 6
ST_AUX = 7
ST_WIN = 8
ST_LOADING = 9
ST_QUIT = 10
ST_QUIT_CONFIRM = 11
ST_SCORE = 12
ST_CALL = 13
ST_DISC = 14
ST_LOGO = 15
ST_TITLE = 16
ST_NAME = 17
ST_READY = 18
ST_ONLINE_SCORE = 19
ST_ONLINE_REGISTER = 20
ST_ONLINE_PIN = 21
ST_ONLINE_CONFIRM = 22
ST_ONLINE_LOCAL_CONFIRM = 23
ST_LOG = 24
ST_LANGUAGE = 25
ST_SETTINGS = 26
ST_DIFFICULTY = 27
ST_NYANDOR_BRIEF = 28
ST_NYANDOR_GUIDE = 29

CALL_PRESETS = [
    "good", "bad", "meh", "skip",
    "try", "use", "id?", "boo",
    "zap", "hmm", "ugh", "yay",
    "wow", "odd", "???", "!!!",
]

B_TAP_FRAMES = 8
BACK_TAP_FRAMES = 8

MENU_ACTIONS = [
    ("Zap", CAT_STICK),
    ("Throw", None),
    ("Eat", CAT_FOOD),
    ("Read", CAT_SCR),
    ("Search", None),
    ("Quaff", CAT_POT),
    ("Wield", CAT_WPN),
    ("Wear", CAT_ARM),
    ("Put on", CAT_RING),
    ("Take off", None),
    ("Discoveries", None),
    ("Trap", None),
    ("Drop", None),
    ("Call", None),
    ("Quit", None),
]
AUX_ACTIONS = []

PAD_ACTION_GRID = (
    ("Zap", "Throw", "Eat"),
    ("Read", "Search", "Quaff"),
    ("Wield", "Wear", "Put on"),
    ("Take off", "Discoveries", "Trap"),
    ("Drop", "Call", "Quit"),
)
PAD_ACTION_INITIAL = "Search"
PACK_GRID_MAX_ROWS = 9


def action_index(actions, name):
    for i, (action_name, _cat) in enumerate(actions):
        if action_name == name:
            return i
    raise ValueError(name)


def pad_action_positions(grid=PAD_ACTION_GRID):
    return {
        name: (x, y)
        for y, row in enumerate(grid)
        for x, name in enumerate(row)
        if name is not None
    }


def pad_menu_initial_index(actions=MENU_ACTIONS):
    return action_index(actions, PAD_ACTION_INITIAL)


def pad_menu_move(current_index, dx, dy, actions=MENU_ACTIONS, grid=PAD_ACTION_GRID):
    positions = pad_action_positions(grid)
    current_name = actions[current_index][0]
    if current_name not in positions:
        return current_index
    x, y = positions[current_name]
    if dx:
        row = grid[y]
        for step in range(1, len(row) + 1):
            name = row[(x + dx * step) % len(row)]
            if name is not None:
                return action_index(actions, name)
    if dy:
        for step in range(1, len(grid) + 1):
            name = grid[(y + dy * step) % len(grid)][x]
            if name is not None:
                return action_index(actions, name)
    return current_index


def pack_grid_shape(count, max_rows=PACK_GRID_MAX_ROWS):
    if count <= 0:
        return (1, 0)
    cols = (count + max_rows - 1) // max_rows
    cols = max(1, min(3, cols))
    rows = (count + cols - 1) // cols
    return (cols, rows)


def pack_grid_pos(index, count, max_rows=PACK_GRID_MAX_ROWS):
    _cols, rows = pack_grid_shape(count, max_rows)
    if rows <= 0:
        return (0, 0)
    return (index // rows, index % rows)


def pack_grid_index(col, row, count, max_rows=PACK_GRID_MAX_ROWS):
    _cols, rows = pack_grid_shape(count, max_rows)
    if rows <= 0:
        return 0
    return min(count - 1, col * rows + row)


def pack_grid_move(current_index, dx, dy, count, max_rows=PACK_GRID_MAX_ROWS):
    if count <= 0:
        return current_index
    cols, rows = pack_grid_shape(count, max_rows)
    col, row = pack_grid_pos(current_index, count, max_rows)
    if dx:
        target_col = (col + dx) % cols
        return pack_grid_index(target_col, row, count, max_rows)
    if dy:
        start = col * rows
        end = min(count, start + rows)
        col_len = max(1, end - start)
        return start + ((row + dy) % col_len)
    return current_index
