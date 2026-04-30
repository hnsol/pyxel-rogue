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
]
AUX_ACTIONS = ["Inventory", "Help", "Search", "Trap", "Pickup", "Language", "Palette", "Quit"]
