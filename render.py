"""Low-level '3D pixel' (voxel) drawing primitives shared across the game.

Each block is drawn as a front face plus an isometric top face (lighter) and
right face (darker), giving a chunky extruded-pixel / voxel look. Light is
assumed to come from the upper-left.
"""

import pygame

import config as C


def lighten(color, f=0.45):
    return tuple(min(255, int(c + (255 - c) * f)) for c in color)


def darken(color, f=0.4):
    return tuple(max(0, int(c * (1 - f))) for c in color)


def draw_voxel_rect(surface, rect, color, depth=None, shadow=False, outline=True):
    """Draw a voxel block whose *front face* is `rect`, extruded up-right."""
    rect = pygame.Rect(rect)
    if depth is None:
        depth = max(3, int(min(rect.w, rect.h) * 0.5))
    x, y, w, h = rect.x, rect.y, rect.w, rect.h

    top_color = lighten(color, 0.5)
    side_color = darken(color, 0.4)
    edge = darken(color, 0.6)

    if shadow:
        sh = pygame.Surface((w + depth + 6, h + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=4)
        surface.blit(sh, (x - 3, y + depth - 2))

    top_poly = [(x, y), (x + depth, y - depth),
                (x + w + depth, y - depth), (x + w, y)]
    right_poly = [(x + w, y), (x + w + depth, y - depth),
                  (x + w + depth, y + h - depth), (x + w, y + h)]

    pygame.draw.polygon(surface, top_color, top_poly)
    pygame.draw.polygon(surface, side_color, right_poly)
    pygame.draw.rect(surface, color, rect)

    if outline:
        pygame.draw.rect(surface, edge, rect, 1)
        pygame.draw.polygon(surface, edge, top_poly, 1)
        pygame.draw.polygon(surface, edge, right_poly, 1)
    return depth


def draw_voxel_cube(surface, cx, cy, size, color, depth=None, shadow=False, outline=True):
    """Voxel block centered (on its front face) at (cx, cy)."""
    half = size // 2
    rect = pygame.Rect(int(cx - half), int(cy - half), size, size)
    return draw_voxel_rect(surface, rect, color, depth=depth,
                           shadow=shadow, outline=outline)


def draw_pixel(surface, cx, cy, size, color):
    """A single flat pixel square centered at (cx, cy)."""
    half = size // 2
    pygame.draw.rect(surface, color, (int(cx - half), int(cy - half), size, size))
