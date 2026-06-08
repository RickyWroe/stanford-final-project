"""Central configuration for Snaky.

All tunable game values live here so balancing the game means editing one file.
"""

# --- Window ---------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "Snaky"

# --- Colors (R, G, B) -----------------------------------------------------
BLACK = (12, 14, 20)
DARK = (22, 26, 36)
FLOOR_A = (26, 30, 42)       # 3D-pixel floor checker tiles
FLOOR_B = (20, 24, 34)
FLOOR_EDGE = (34, 40, 54)
WHITE = (240, 244, 248)
GREY = (120, 128, 140)
LIGHT_GREY = (180, 186, 196)
ENEMY_COLOR = (200, 60, 70)
ENEMY_DARK = (140, 36, 44)
MOUSE_COLOR = (220, 220, 225)
MOUSE_EAR = (235, 170, 180)
OBSTACLE_COLOR = (70, 78, 96)
OBSTACLE_EDGE = (96, 104, 124)
LIFE_BAR_BG = (60, 30, 34)
LIFE_BAR_FILL = (210, 70, 80)
BOOST_COLOR = (255, 214, 90)

# --- Snake types (the four selectable snakes) -----------------------------
# Each entry: display name + body color + a slightly darker outline color.
SNAKE_TYPES = [
    {"name": "Emerald", "color": (60, 200, 120), "dark": (36, 140, 84)},
    {"name": "Azure", "color": (70, 150, 235), "dark": (44, 100, 170)},
    {"name": "Amber", "color": (240, 180, 60), "dark": (180, 130, 36)},
    {"name": "Violet", "color": (170, 110, 230), "dark": (118, 70, 170)},
]

# --- Snake physics --------------------------------------------------------
SEGMENT_RADIUS = 11          # radius of each body circle (player base size)
SEGMENT_SPACING = 9          # pixels between sampled body segments along the trail
PLAYER_START_LENGTH = 7      # number of body segments at start
PLAYER_SPEED = 200.0         # pixels per second (base)
ENEMY_SPEED = 178.0          # slightly slower than the player so it's winnable

# --- Speed boost (from eating a mouse) ------------------------------------
BOOST_MULTIPLIER = 1.7
BOOST_DURATION = 2.0         # seconds

# --- Enemy life / win condition -------------------------------------------
ENEMY_MAX_LIFE = 100.0
MICE_TO_WIN = 5
LIFE_DRAIN_PER_MOUSE = ENEMY_MAX_LIFE / MICE_TO_WIN
ENEMY_SEGMENT_RADIUS = 12

# --- Capture (lose) -------------------------------------------------------
CAPTURE_RADIUS = 18          # enemy head within this of a player segment => caught

# --- Field contents -------------------------------------------------------
# Obstacles are thin "lines" (bars), placed horizontally or vertically.
OBSTACLE_COUNT = 8
OBSTACLE_THICKNESS = 16
OBSTACLE_MIN_LEN = 90
OBSTACLE_MAX_LEN = 240
MOUSE_RADIUS = 9
SAFE_SPAWN_MARGIN = 90       # keep obstacles/mice away from start positions

# --- Enemy steering & adaptive learning -----------------------------------
# The chaser chases in a straight line when it can see the player; when a line
# obstacle blocks the line of sight it steers to the nearer open end of that
# line and rounds it. A light reinforcement loop makes it commit harder as
# detours succeed, and flip to the other end if one drags on.
AVOID_RADIUS = 90            # how far the enemy "feels" walls for slide-off
AVOID_STRENGTH = 0.6         # weight of the repulsion vs. the chase pull
FLIP_TIME = 2.2             # if blocked this long, try rounding the other end
BIAS_START = 0.8            # base commitment to the go-around waypoint
BIAS_MAX = 2.5             # learned commitment grows toward this as it succeeds
BIAS_REINFORCE = 0.12       # bump to commitment each time a detour clears

# --- HUD / layout ---------------------------------------------------------
HUD_HEIGHT = 56              # reserved strip at the top for the life bar
PLAY_TOP = HUD_HEIGHT        # gameplay area starts below the HUD
