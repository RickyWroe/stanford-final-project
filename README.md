# 🐍 Snaky

A small arcade chase game built with Python + Pygame.

Pick one of four snakes, name it, then survive a relentless AI chaser. Eat mice to drain the
chaser's life bar — drop it to **0 to win**. Get caught and it's game over.

## Gameplay

- **Free 8‑direction movement** — your snake moves continuously; steer with the arrow keys or WASD.
- **One AI chaser** hunts your head. If it catches you, you lose.
- **Solid walls** — the snake stops and slides along the screen edges (no wall death).
- **Obstacles** are solid and block *both* you and the chaser — juke it around them.
- **Mice** give a short **speed boost** and drain ~1/5 of the chaser's life bar each.
- **Win** by draining the chaser's life to 0 (about 5 mice).

## Controls

| Key | Action |
| --- | --- |
| Arrow keys / WASD | Steer (8 directions) |
| Enter | Advance / confirm |
| Backspace | Edit the name |
| ← → (snake select) | Change snake |
| R | Play again (on the end screen) |
| Esc / Q | Back / quit |

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> This project uses **`pygame-ce`** (the community edition of Pygame), which ships up‑to‑date
> wheels for recent Python versions. It exposes the same `import pygame` API. If installation
> fails on a very new Python release, create the venv with Python 3.13.

## Run

```bash
python main.py
```
