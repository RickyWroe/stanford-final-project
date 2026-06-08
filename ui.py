"""Screen rendering, HUD and a small text-input widget for Snaky."""

import math

import pygame

import config as C
import render


class Fonts:
    """Bundle of fonts; create after pygame.font is initialised."""

    def __init__(self):
        self.title = pygame.font.SysFont("arialroundedmtbold,arial", 76, bold=True)
        self.big = pygame.font.SysFont("arial", 48, bold=True)
        self.medium = pygame.font.SysFont("arial", 30, bold=True)
        self.small = pygame.font.SysFont("arial", 22)
        self.tiny = pygame.font.SysFont("arial", 18, bold=True)


def _blit_center(surface, font, text, color, cx, cy):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(cx, cy))
    surface.blit(img, rect)
    return rect


_floor_cache = None


def _build_floor():
    """A chunky 3D-pixel checkerboard floor, built once and cached."""
    surf = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT - C.PLAY_TOP))
    tile = 32
    for ty in range(0, surf.get_height(), tile):
        for tx in range(0, surf.get_width(), tile):
            checker = ((tx // tile) + (ty // tile)) % 2 == 0
            rect = pygame.Rect(tx, ty, tile, tile)
            surf.fill(C.FLOOR_A if checker else C.FLOOR_B, rect)
            pygame.draw.line(surf, C.FLOOR_EDGE, rect.topleft, (rect.right, rect.top))
            pygame.draw.line(surf, C.FLOOR_EDGE, rect.topleft, (rect.left, rect.bottom))
    return surf


def draw_background(surface, with_grid=True):
    surface.fill(C.BLACK)
    if with_grid:
        global _floor_cache
        if _floor_cache is None:
            _floor_cache = _build_floor()
        surface.blit(_floor_cache, (0, C.PLAY_TOP))


def _draw_snake_preview(surface, snake_type, cx, cy, segments=6, radius=14, wiggle=0.0):
    """A little voxel snake drawn in the given type's colors."""
    for i in range(segments - 1, -1, -1):
        offset = i * (radius + 4)
        px = cx - offset + math.sin(wiggle + i * 0.6) * 6
        py = cy + math.sin(wiggle * 1.3 + i * 0.8) * 4
        r = radius if i == 0 else max(5, int(radius * (0.65 + 0.35 * (1 - i / segments))))
        render.draw_voxel_cube(surface, px, py, r * 2, snake_type["color"], shadow=(i == 0))
    render.draw_pixel(surface, cx + 4, cy - radius * 0.5, 4, C.WHITE)
    render.draw_pixel(surface, cx + 4, cy - radius * 0.5, 2, C.BLACK)


# --- Screens -------------------------------------------------------------

def draw_greeting(surface, fonts, t):
    draw_background(surface, with_grid=False)
    _draw_snake_preview(surface, C.SNAKE_TYPES[0], C.SCREEN_WIDTH // 2 + 60,
                        C.SCREEN_HEIGHT // 2 - 110, segments=7, radius=18, wiggle=t * 3)
    _blit_center(surface, fonts.title, "Welcome to Snaky",
                 C.SNAKE_TYPES[0]["color"], C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2)
    _blit_center(surface, fonts.small,
                 "Eat mice to drain the chaser's life to zero.  Don't get caught!",
                 C.LIGHT_GREY, C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 60)
    if int(t * 2) % 2 == 0:
        _blit_center(surface, fonts.medium, "Press ENTER to start", C.WHITE,
                     C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 130)


def draw_select(surface, fonts, selected_index, t):
    draw_background(surface, with_grid=False)
    _blit_center(surface, fonts.big, "Choose your snake", C.WHITE,
                 C.SCREEN_WIDTH // 2, 90)

    n = len(C.SNAKE_TYPES)
    card_w, card_h = 180, 200
    gap = 30
    total = n * card_w + (n - 1) * gap
    start_x = (C.SCREEN_WIDTH - total) // 2
    y = C.SCREEN_HEIGHT // 2 - card_h // 2 + 10

    for i, st in enumerate(C.SNAKE_TYPES):
        x = start_x + i * (card_w + gap)
        rect = pygame.Rect(x, y, card_w, card_h)
        selected = i == selected_index
        bg = (40, 46, 60) if selected else (26, 30, 40)
        pygame.draw.rect(surface, bg, rect, border_radius=14)
        border = st["color"] if selected else (60, 66, 80)
        pygame.draw.rect(surface, border, rect, width=4 if selected else 2, border_radius=14)
        _draw_snake_preview(surface, st, rect.centerx + 20, rect.centery - 10,
                            segments=5, radius=15, wiggle=t * 3 + i)
        _blit_center(surface, fonts.medium, st["name"], st["color"],
                     rect.centerx, rect.bottom - 32)

    _blit_center(surface, fonts.small, "← →  to choose      ENTER to confirm",
                 C.LIGHT_GREY, C.SCREEN_WIDTH // 2, y + card_h + 70)


def draw_name_input(surface, fonts, snake_type, text, t):
    draw_background(surface, with_grid=False)
    _blit_center(surface, fonts.big, "Name your snake", snake_type["color"],
                 C.SCREEN_WIDTH // 2, 120)
    _draw_snake_preview(surface, snake_type, C.SCREEN_WIDTH // 2 + 30, 230,
                        segments=6, radius=18, wiggle=t * 3)

    box = pygame.Rect(0, 0, 460, 64)
    box.center = (C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 40)
    pygame.draw.rect(surface, (30, 34, 46), box, border_radius=10)
    pygame.draw.rect(surface, snake_type["color"], box, width=3, border_radius=10)

    cursor = "|" if int(t * 2) % 2 == 0 else " "
    shown = (text + cursor) if text or cursor else "_"
    label = shown if text else f"Type a name{cursor}"
    color = C.WHITE if text else C.GREY
    _blit_center(surface, fonts.medium, label, color, box.centerx, box.centery)

    _blit_center(surface, fonts.small, "ENTER to continue", C.LIGHT_GREY,
                 C.SCREEN_WIDTH // 2, box.bottom + 60)


def draw_confirm(surface, fonts, snake_type, name, t):
    draw_background(surface, with_grid=False)
    _blit_center(surface, fonts.big, "Ready?", C.WHITE, C.SCREEN_WIDTH // 2, 110)
    _draw_snake_preview(surface, snake_type, C.SCREEN_WIDTH // 2 + 30,
                        C.SCREEN_HEIGHT // 2 - 30, segments=7, radius=22, wiggle=t * 3)
    _blit_center(surface, fonts.medium, f'"{name}"  the  {snake_type["name"]}  snake',
                 snake_type["color"], C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 50)
    _blit_center(surface, fonts.small, "ENTER to confirm        ESC to go back",
                 C.LIGHT_GREY, C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 120)


def draw_countdown(surface, draw_world, fonts, label, scale):
    """Draw the frozen world, then a big pulsing countdown number on top."""
    draw_world(surface)
    overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    surface.blit(overlay, (0, 0))
    size = int(120 * scale)
    font = pygame.font.SysFont("arial", max(20, size), bold=True)
    _blit_center(surface, font, label, C.WHITE, C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2)


def draw_floating_name(surface, fonts, player):
    img = fonts.tiny.render(player.name, True, C.WHITE)
    rect = img.get_rect(center=(int(player.x), int(player.y) - player.radius - 16))
    pad = pygame.Rect(rect.left - 6, rect.top - 3, rect.width + 12, rect.height + 6)
    bg = pygame.Surface(pad.size, pygame.SRCALPHA)
    bg.fill((0, 0, 0, 150))
    surface.blit(bg, pad.topleft)
    surface.blit(img, rect)


def draw_hud(surface, fonts, enemy_life, mice_eaten):
    bar = pygame.Rect(0, 0, C.SCREEN_WIDTH, C.HUD_HEIGHT)
    pygame.draw.rect(surface, (18, 20, 28), bar)
    pygame.draw.line(surface, (40, 44, 56), (0, C.HUD_HEIGHT), (C.SCREEN_WIDTH, C.HUD_HEIGHT), 2)

    # enemy life bar
    label = fonts.tiny.render("CHASER", True, C.ENEMY_COLOR)
    surface.blit(label, (20, C.HUD_HEIGHT // 2 - label.get_height() // 2))
    bx = 110
    bw = 380
    track = pygame.Rect(bx, C.HUD_HEIGHT // 2 - 10, bw, 20)
    pygame.draw.rect(surface, C.LIFE_BAR_BG, track, border_radius=10)
    frac = max(0.0, enemy_life / C.ENEMY_MAX_LIFE)
    if frac > 0:
        fill = pygame.Rect(bx, track.top, int(bw * frac), 20)
        pygame.draw.rect(surface, C.LIFE_BAR_FILL, fill, border_radius=10)
    pygame.draw.rect(surface, (90, 40, 46), track, width=2, border_radius=10)

    # mice counter
    text = fonts.tiny.render(f"Mice eaten: {mice_eaten}/{C.MICE_TO_WIN}", True, C.LIGHT_GREY)
    surface.blit(text, (C.SCREEN_WIDTH - text.get_width() - 24,
                        C.HUD_HEIGHT // 2 - text.get_height() // 2))


def draw_game_over(surface, draw_world, fonts, won, mice_eaten, t):
    draw_world(surface)
    overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    if won:
        _blit_center(surface, fonts.title, "You Win!", (90, 220, 130),
                     C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 - 70)
        msg = "You drained the chaser's life to zero."
    else:
        _blit_center(surface, fonts.title, "Caught!", C.ENEMY_COLOR,
                     C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 - 70)
        msg = "The chaser got you."
    _blit_center(surface, fonts.small, msg, C.LIGHT_GREY,
                 C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2)
    _blit_center(surface, fonts.small, f"Mice eaten: {mice_eaten}/{C.MICE_TO_WIN}",
                 C.LIGHT_GREY, C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 36)
    if int(t * 2) % 2 == 0:
        _blit_center(surface, fonts.medium, "R to play again      ESC to quit",
                     C.WHITE, C.SCREEN_WIDTH // 2, C.SCREEN_HEIGHT // 2 + 110)


class TextInput:
    """Minimal single-line text field for the name entry screen."""

    def __init__(self, max_len=14):
        self.text = ""
        self.max_len = max_len

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode and event.unicode.isprintable():
            if len(self.text) < self.max_len and event.unicode not in ("\r", "\n", "\t"):
                self.text += event.unicode

    @property
    def value(self):
        return self.text.strip()
