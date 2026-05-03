from rogue_items import CAT_ARM, CAT_FOOD, CAT_POT, CAT_RING, CAT_SCR, CAT_STICK, CAT_WPN

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

CALL_PRESETS = [
    "good", "bad", "meh", "skip",
    "try", "use", "id?", "boo",
    "zap", "hmm", "ugh", "yay",
    "wow", "odd", "???", "!!!",
]

B_TAP_FRAMES = 8
BACK_TAP_FRAMES = 8

MENU_ACTIONS = [
    ("Quaff", CAT_POT),
    ("Read", CAT_SCR),
    ("Eat", CAT_FOOD),
    ("Wield", CAT_WPN),
    ("Wear", CAT_ARM),
    ("Put on", CAT_RING),
    ("Take off", None),
    ("Zap", CAT_STICK),
    ("Throw", None),
    ("Drop", None),
    ("Call", None),
    ("Discoveries", None),
]
AUX_ACTIONS = ["Inventory", "Help", "Search", "Trap", "Pickup", "Language", "Palette", "Quit"]

PAD_ACTION_GRID = (
    ("Zap", "Throw", "Put on"),
    ("Quaff", "Eat", "Read"),
    ("Wield", "Wear", "Take off"),
    ("Call", "Discoveries", "Drop"),
)
PAD_ACTION_INITIAL = "Eat"


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
