"""Snaky — a Pygame chase game.

Run from a terminal:  python main.py

You steer a snake in 8 directions. A single AI chaser hunts you. Eat mice to
gain a speed boost and drain the chaser's life bar; drop it to zero to win.
Get caught and it's game over.
"""

import sys

import pygame

import config as C
import ui
from entities import spawn_obstacles, spawn_mouse
from snake import PlayerSnake, EnemySnake

# Game states
GREETING = "greeting"
SELECT = "select"
NAME_INPUT = "name_input"
CONFIRM = "confirm"
COUNTDOWN = "countdown"
PLAYING = "playing"
GAME_OVER = "game_over"

# Countdown beats: "3", "2", "1", "GO!"
BEAT = 0.8
COUNT_LABELS = ["3", "2", "1", "GO!"]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(C.TITLE)
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = ui.Fonts()

        self.state = GREETING
        self.t = 0.0  # global animation clock

        self.selected_index = 0
        self.text_input = ui.TextInput()
        self.player_name = "Sly"

        # round objects (created in start_round)
        self.player = None
        self.enemy = None
        self.obstacles = []
        self.mouse = None
        self.mice_eaten = 0
        self.countdown_t = 0.0
        self.won = False

    # --- round lifecycle -------------------------------------------------
    def start_round(self):
        snake_type = C.SNAKE_TYPES[self.selected_index]
        play_mid_y = (C.PLAY_TOP + C.SCREEN_HEIGHT) // 2

        player_start = (150, play_mid_y)
        enemy_start = (C.SCREEN_WIDTH - 150, C.SCREEN_HEIGHT - 130)

        self.player = PlayerSnake(*player_start, snake_type, self.player_name)
        self.enemy = EnemySnake(*enemy_start, player_pos=player_start)
        self.obstacles = spawn_obstacles(avoid_points=[player_start, enemy_start])
        self.mouse = spawn_mouse(self.obstacles,
                                 avoid_points=[player_start, enemy_start])
        self.mice_eaten = 0
        self.won = False
        self.countdown_t = 0.0
        self.state = COUNTDOWN

    # --- per-state updates ----------------------------------------------
    def update_countdown(self, dt):
        self.countdown_t += dt
        if self.countdown_t >= BEAT * len(COUNT_LABELS):
            self.state = PLAYING

    def update_play(self, dt):
        keys = pygame.key.get_pressed()
        self.player.step(dt, keys, self.obstacles)
        self.enemy.step(dt, self.player, self.obstacles)
        self.mouse.update(dt)

        # eat a mouse
        if self.mouse.eaten_by(self.player.x, self.player.y, self.player.radius):
            self.mice_eaten += 1
            self.enemy.life -= C.LIFE_DRAIN_PER_MOUSE
            self.player.trigger_boost()
            if self.enemy.life <= 0:
                self.enemy.life = 0
                self.end_round(won=True)
                return
            self.mouse = spawn_mouse(
                self.obstacles, avoid_points=[self.player.head, self.enemy.head]
            )

        # caught?
        if self.enemy.caught(self.player):
            self.end_round(won=False)

    def end_round(self, won):
        self.won = won
        self.state = GAME_OVER

    # --- rendering -------------------------------------------------------
    def draw_world(self, surface):
        ui.draw_background(surface, with_grid=True)
        for o in self.obstacles:
            o.draw(surface)
        self.mouse.draw(surface)
        self.enemy.draw(surface)
        self.player.draw(surface)
        ui.draw_floating_name(surface, self.fonts, self.player)
        ui.draw_hud(surface, self.fonts, self.enemy.life, self.mice_eaten)

    def render(self):
        s = self.screen
        if self.state == GREETING:
            ui.draw_greeting(s, self.fonts, self.t)
        elif self.state == SELECT:
            ui.draw_select(s, self.fonts, self.selected_index, self.t)
        elif self.state == NAME_INPUT:
            ui.draw_name_input(s, self.fonts, C.SNAKE_TYPES[self.selected_index],
                               self.text_input.text, self.t)
        elif self.state == CONFIRM:
            ui.draw_confirm(s, self.fonts, C.SNAKE_TYPES[self.selected_index],
                            self.player_name, self.t)
        elif self.state == COUNTDOWN:
            beat = min(len(COUNT_LABELS) - 1, int(self.countdown_t / BEAT))
            frac = (self.countdown_t - beat * BEAT) / BEAT
            scale = 1.0 + 0.5 * (1 - frac)
            ui.draw_countdown(s, self.draw_world, self.fonts, COUNT_LABELS[beat], scale)
        elif self.state == PLAYING:
            self.draw_world(s)
        elif self.state == GAME_OVER:
            ui.draw_game_over(s, self.draw_world, self.fonts, self.won,
                              self.mice_eaten, self.t)
        pygame.display.flip()

    # --- input -----------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        if event.type != pygame.KEYDOWN:
            return

        if self.state == GREETING:
            if event.key == pygame.K_RETURN:
                self.state = SELECT
            elif event.key == pygame.K_ESCAPE:
                self.quit()

        elif self.state == SELECT:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_index = (self.selected_index - 1) % len(C.SNAKE_TYPES)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_index = (self.selected_index + 1) % len(C.SNAKE_TYPES)
            elif event.key == pygame.K_RETURN:
                self.text_input.text = self.player_name if self.player_name != "Sly" else ""
                self.state = NAME_INPUT
            elif event.key == pygame.K_ESCAPE:
                self.state = GREETING

        elif self.state == NAME_INPUT:
            if event.key == pygame.K_RETURN:
                self.player_name = self.text_input.value or "Sly"
                self.state = CONFIRM
            elif event.key == pygame.K_ESCAPE:
                self.state = SELECT
            else:
                self.text_input.handle_event(event)

        elif self.state == CONFIRM:
            if event.key == pygame.K_RETURN:
                self.start_round()
            elif event.key == pygame.K_ESCAPE:
                self.state = NAME_INPUT

        elif self.state == PLAYING:
            if event.key == pygame.K_ESCAPE:
                self.state = GREETING

        elif self.state == GAME_OVER:
            if event.key == pygame.K_r:
                self.start_round()
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.quit()

    # --- loop ------------------------------------------------------------
    def update(self, dt):
        if self.state == COUNTDOWN:
            self.update_countdown(dt)
        elif self.state == PLAYING:
            self.update_play(dt)

    def run(self):
        while True:
            dt = min(self.clock.tick(C.FPS) / 1000.0, 0.05)
            self.t += dt
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.render()

    def quit(self):
        pygame.quit()
        sys.exit(0)


def main():
    Game().run()


if __name__ == "__main__":
    main()
