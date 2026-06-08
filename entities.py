"""Field entities for Snaky: obstacles and mice, plus spawn helpers."""

import math
import random

import pygame

import config as C
import render


def _circle_hits_rect(cx, cy, r, rect):
    """True if a circle (cx, cy, r) overlaps a pygame.Rect."""
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return dx * dx + dy * dy < r * r


class Obstacle:
    """A solid line (thin bar) that stops both snakes. Drawn as a 3D-pixel bar."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

    def blocks_circle(self, cx, cy, r):
        return _circle_hits_rect(cx, cy, r, self.rect)

    def draw(self, surface):
        render.draw_voxel_rect(surface, self.rect, C.OBSTACLE_COLOR,
                               depth=8, shadow=True)


class Mouse:
    """A pickup. Eating it boosts the player and drains the enemy's life."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = C.MOUSE_RADIUS
        self._t = 0.0  # animation timer for a gentle bob

    def update(self, dt):
        self._t += dt

    def eaten_by(self, head_x, head_y, head_r):
        dx = self.x - head_x
        dy = self.y - head_y
        reach = self.radius + head_r
        return dx * dx + dy * dy <= reach * reach

    def draw(self, surface):
        bob = math.sin(self._t * 4.0) * 2.0
        cx, cy = int(self.x), int(self.y + bob)
        s = self.radius * 2
        # ears (small voxel cubes)
        render.draw_voxel_cube(surface, cx - self.radius, cy - self.radius,
                               s // 2, C.MOUSE_EAR)
        render.draw_voxel_cube(surface, cx + self.radius, cy - self.radius,
                               s // 2, C.MOUSE_EAR)
        # body
        render.draw_voxel_cube(surface, cx, cy, s, C.MOUSE_COLOR, shadow=True)
        # eye pixel
        render.draw_pixel(surface, cx + 3, cy - 1, 3, C.BLACK)


def _play_area():
    """Bounds of the gameplay area (below the HUD)."""
    return pygame.Rect(0, C.PLAY_TOP, C.SCREEN_WIDTH, C.SCREEN_HEIGHT - C.PLAY_TOP)


def spawn_obstacles(avoid_points, count=C.OBSTACLE_COUNT):
    """Place non-overlapping line obstacles, keeping clear of `avoid_points`."""
    area = _play_area()
    thickness = C.OBSTACLE_THICKNESS
    obstacles = []
    attempts = 0
    while len(obstacles) < count and attempts < count * 80:
        attempts += 1
        length = random.randint(C.OBSTACLE_MIN_LEN, C.OBSTACLE_MAX_LEN)
        if random.random() < 0.5:           # horizontal line
            w, h = length, thickness
        else:                               # vertical line
            w, h = thickness, length
        x = random.randint(area.left + 24, area.right - w - 24)
        y = random.randint(area.top + 24, area.bottom - h - 24)
        rect = pygame.Rect(x, y, w, h)

        # keep away from start positions / each other
        if any(_circle_hits_rect(px, py, C.SAFE_SPAWN_MARGIN, rect) for px, py in avoid_points):
            continue
        if any(rect.inflate(54, 54).colliderect(o.rect) for o in obstacles):
            continue
        obstacles.append(Obstacle(rect))
    return obstacles


def random_free_position(radius, obstacles, avoid_points=None, min_clear=0.0):
    """Find a point inside the play area not inside an obstacle.

    `avoid_points` (and `min_clear`) let callers keep a mouse away from the snakes.
    """
    area = _play_area()
    avoid_points = avoid_points or []
    for _ in range(300):
        x = random.randint(area.left + radius + 4, area.right - radius - 4)
        y = random.randint(area.top + radius + 4, area.bottom - radius - 4)
        if any(o.blocks_circle(x, y, radius + 6) for o in obstacles):
            continue
        if any(math.hypot(x - px, y - py) < min_clear for px, py in avoid_points):
            continue
        return x, y
    # Fallback: center of the play area.
    return area.centerx, area.centery


def spawn_mouse(obstacles, avoid_points=None):
    x, y = random_free_position(
        C.MOUSE_RADIUS, obstacles, avoid_points=avoid_points, min_clear=120
    )
    return Mouse(x, y)
