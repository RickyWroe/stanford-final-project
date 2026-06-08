"""Snake actors for Snaky.

A snake's body is a *trail* of past head positions; body segments are sampled
from that trail at a fixed arc-length spacing (slither-style). This works
naturally with free 8-direction movement.
"""

import math

import pygame

import config as C
import render


def _normalize(dx, dy):
    mag = math.hypot(dx, dy)
    if mag < 1e-6:
        return 0.0, 0.0
    return dx / mag, dy / mag


def _rotate(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return x * c - y * s, x * s + y * c


def _escape_targets(rect):
    """The two points just past the open ends of a line obstacle."""
    m = 46
    if rect.height >= rect.width:                       # vertical line
        return [(rect.centerx, rect.top - m), (rect.centerx, rect.bottom + m)]
    return [(rect.left - m, rect.centery), (rect.right + m, rect.centery)]


class BaseSnake:
    """Shared movement, trail sampling, solid collision and drawing."""

    def __init__(self, x, y, heading, length, radius, color, dark, speed):
        self.x = float(x)
        self.y = float(y)
        self.heading = _normalize(*heading)
        if self.heading == (0.0, 0.0):
            self.heading = (1.0, 0.0)
        self.length = length
        self.radius = radius
        self.color = color
        self.dark = dark
        self.speed = speed
        self.trail = []
        self._seed_trail()

    # --- trail -----------------------------------------------------------
    def _max_trail(self):
        return self.length * 8 + 40

    def _seed_trail(self):
        """Lay down a straight starting tail behind the head."""
        hx, hy = self.heading
        step = 3.0
        n = self.length * 6
        self.trail = [(self.x - hx * i * step, self.y - hy * i * step)
                      for i in range(n, 0, -1)]
        self.trail.append((self.x, self.y))

    def body_points(self):
        """Centers of the body circles, head first, evenly spaced along the trail."""
        if len(self.trail) < 2:
            return [(self.x, self.y)] * self.length
        poly = list(reversed(self.trail))  # head first
        points = [poly[0]]
        targets = [C.SEGMENT_SPACING * k for k in range(1, self.length)]
        ti = 0
        acc = 0.0
        for i in range(1, len(poly)):
            x0, y0 = poly[i - 1]
            x1, y1 = poly[i]
            seg = math.hypot(x1 - x0, y1 - y0)
            if seg == 0:
                continue
            while ti < len(targets) and acc + seg >= targets[ti]:
                t = (targets[ti] - acc) / seg
                points.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
                ti += 1
            acc += seg
            if ti >= len(targets):
                break
        while len(points) < self.length:
            points.append(poly[-1])
        return points

    @property
    def head(self):
        return self.x, self.y

    # --- collision -------------------------------------------------------
    def _blocked(self, cx, cy, obstacles):
        r = self.radius
        if cx - r < 0 or cx + r > C.SCREEN_WIDTH:
            return True
        if cy - r < C.PLAY_TOP or cy + r > C.SCREEN_HEIGHT:
            return True
        return any(o.blocks_circle(cx, cy, r) for o in obstacles)

    def _move_with_heading(self, dt, obstacles, hx, hy):
        """Try to move along (hx, hy), resolving walls/obstacles per axis.

        Returns True if the head actually moved.
        """
        dx = hx * self.speed * dt
        dy = hy * self.speed * dt
        moved = False
        if dx and not self._blocked(self.x + dx, self.y, obstacles):
            self.x += dx
            moved = True
        if dy and not self._blocked(self.x, self.y + dy, obstacles):
            self.y += dy
            moved = True
        return moved

    def _record_trail(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self._max_trail():
            self.trail = self.trail[-self._max_trail():]

    def advance(self, dt, obstacles):
        """Move along the current heading, resolving walls/obstacles per axis."""
        self._move_with_heading(dt, obstacles, self.heading[0], self.heading[1])
        self._record_trail()

    # --- drawing ---------------------------------------------------------
    def _draw_body(self, surface, head_color=None):
        points = self.body_points()
        # tail -> head so the head sits on top
        for i in range(len(points) - 1, 0, -1):
            px, py = points[i]
            # taper slightly toward the tail
            taper = 0.6 + 0.4 * (1 - i / max(1, len(points)))
            size = max(6, int(self.radius * 2 * taper))
            render.draw_voxel_cube(surface, px, py, size, self.color)
        self._draw_head(surface, points[0], head_color)

    def _draw_head(self, surface, pos, head_color):
        hx, hy = int(pos[0]), int(pos[1])
        size = (self.radius + 2) * 2
        color = head_color if head_color else self.color
        render.draw_voxel_cube(surface, hx, hy, size, color, shadow=True)
        # eyes as little pixels, offset toward the heading (on the top face)
        hxn, hyn = self.heading
        perp = (-hyn, hxn)
        eye_fwd = self.radius * 0.3
        eye_side = self.radius * 0.5
        for sign in (1, -1):
            ex = hx + hxn * eye_fwd + perp[0] * eye_side * sign
            ey = hy + hyn * eye_fwd + perp[1] * eye_side * sign - self.radius * 0.3
            render.draw_pixel(surface, ex, ey, 4, C.WHITE)
            render.draw_pixel(surface, ex, ey, 2, C.BLACK)

    def draw(self, surface):
        self._draw_body(surface)


class PlayerSnake(BaseSnake):
    """The snake the human steers. 8-direction input + speed-boost timer."""

    def __init__(self, x, y, snake_type, name):
        super().__init__(
            x, y, heading=(1.0, 0.0), length=C.PLAYER_START_LENGTH,
            radius=C.SEGMENT_RADIUS, color=snake_type["color"],
            dark=snake_type["dark"], speed=C.PLAYER_SPEED,
        )
        self.name = name
        self.boost_timer = 0.0

    @property
    def is_boosting(self):
        return self.boost_timer > 0.0

    def trigger_boost(self):
        self.boost_timer = C.BOOST_DURATION

    def step(self, dt, keys, obstacles):
        dx = dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        if dx or dy:
            self.heading = _normalize(dx, dy)

        if self.boost_timer > 0.0:
            self.boost_timer = max(0.0, self.boost_timer - dt)
            self.speed = C.PLAYER_SPEED * C.BOOST_MULTIPLIER
        else:
            self.speed = C.PLAYER_SPEED

        self.advance(dt, obstacles)

    def draw(self, surface):
        head_color = C.BOOST_COLOR if self.is_boosting else None
        self._draw_body(surface, head_color=head_color)


class EnemySnake(BaseSnake):
    """AI chaser. Steers toward the player while avoiding obstacles and walls."""

    def __init__(self, x, y, player_pos):
        heading = _normalize(player_pos[0] - x, player_pos[1] - y)
        super().__init__(
            x, y, heading=heading, length=9, radius=C.ENEMY_SEGMENT_RADIUS,
            color=C.ENEMY_COLOR, dark=C.ENEMY_DARK, speed=C.ENEMY_SPEED,
        )
        self.life = C.ENEMY_MAX_LIFE
        # --- adaptive navigation state (basic reinforcement) ---
        self.bias = C.BIAS_START       # learned commitment to the go-around path
        self.was_blocked = False       # had line-of-sight blocked last frame?
        self.blocked_time = 0.0        # seconds the current detour has lasted
        self.flipped = False           # already switched to the other end?

    def _avoidance(self, obstacles):
        """Repulsion vector away from nearby obstacles and screen edges."""
        ax = ay = 0.0
        R = C.AVOID_RADIUS
        for o in obstacles:
            rect = o.rect
            nx = max(rect.left, min(self.x, rect.right))
            ny = max(rect.top, min(self.y, rect.bottom))
            dx = self.x - nx
            dy = self.y - ny
            dist = math.hypot(dx, dy)
            if 0 < dist < R:
                w = (1 - dist / R)
                ax += (dx / dist) * w
                ay += (dy / dist) * w
        # walls
        if self.x < R:
            ax += (1 - self.x / R)
        if C.SCREEN_WIDTH - self.x < R:
            ax -= (1 - (C.SCREEN_WIDTH - self.x) / R)
        if self.y - C.PLAY_TOP < R:
            ay += (1 - (self.y - C.PLAY_TOP) / R)
        if C.SCREEN_HEIGHT - self.y < R:
            ay -= (1 - (C.SCREEN_HEIGHT - self.y) / R)
        return ax, ay

    def _blocking_obstacle(self, px, py, obstacles):
        """The nearest line obstacle that sits on the straight path to (px, py)."""
        best, best_d = None, 1e18
        for o in obstacles:
            if o.rect.clipline(int(self.x), int(self.y), int(px), int(py)):
                d = math.hypot(o.rect.centerx - self.x, o.rect.centery - self.y)
                if d < best_d:
                    best, best_d = o, d
        return best

    def _aim(self, player, obstacles):
        """Pick a heading: chase directly, or steer around a blocking line.

        The adaptive part: every time a detour clears the line of sight the
        chaser reinforces its commitment (`bias`); if a single detour drags on
        past FLIP_TIME it learns to round the *other* end instead.
        """
        cx, cy = _normalize(player.x - self.x, player.y - self.y)
        ax, ay = self._avoidance(obstacles)
        blocking = self._blocking_obstacle(player.x, player.y, obstacles)

        if blocking is None:
            if self.was_blocked:                    # a detour just succeeded
                self.bias = min(C.BIAS_MAX, self.bias + C.BIAS_REINFORCE)
            self.was_blocked = False
            self.blocked_time = 0.0
            self.flipped = False
            return _normalize(cx + ax * C.AVOID_STRENGTH, cy + ay * C.AVOID_STRENGTH)

        # blocked: head for an open end of the line and round it
        self.was_blocked = True
        self.blocked_time += 1 / C.FPS
        targets = _escape_targets(blocking.rect)
        targets.sort(key=lambda p: math.hypot(p[0] - self.x, p[1] - self.y))
        target = targets[0]
        if self.blocked_time > C.FLIP_TIME:         # this end isn't working out
            target = targets[1]
            if not self.flipped:
                self.bias = min(C.BIAS_MAX, self.bias + 0.1)
                self.flipped = True
        gx, gy = _normalize(target[0] - self.x, target[1] - self.y)
        w = 1.0 + self.bias
        return _normalize(gx * w + ax * C.AVOID_STRENGTH, gy * w + ay * C.AVOID_STRENGTH)

    def step(self, dt, player, obstacles):
        hx, hy = self._aim(player, obstacles)
        if (hx, hy) != (0.0, 0.0):
            self.heading = (hx, hy)

        # shrink as life drains (visual feedback)
        self.length = max(4, int(4 + 5 * (self.life / C.ENEMY_MAX_LIFE)))

        # move, but never get stranded: if blocked, rotate until something frees
        moved = self._move_with_heading(dt, obstacles, self.heading[0], self.heading[1])
        if not moved:
            self._unstick(dt, obstacles)
        self._record_trail()

    def _unstick(self, dt, obstacles):
        """Sweep the heading around until a free direction is found.

        Guarantees the chaser keeps moving whenever *any* direction is open,
        so it can never be permanently trapped behind a line or in a corner.
        """
        base = self.heading
        for step_deg in range(20, 200, 20):
            for s in (1, -1):
                rx, ry = _rotate(base[0], base[1], step_deg * s)
                if self._move_with_heading(dt, obstacles, rx, ry):
                    self.heading = _normalize(rx, ry)
                    return True
        for rx, ry in ((1, 0), (-1, 0), (0, 1), (0, -1)):   # last resort
            if self._move_with_heading(dt, obstacles, rx, ry):
                self.heading = (float(rx), float(ry))
                return True
        return False

    def caught(self, player):
        """True if the enemy head touches any player body segment."""
        for px, py in player.body_points():
            if math.hypot(self.x - px, self.y - py) <= C.CAPTURE_RADIUS:
                return True
        return False
