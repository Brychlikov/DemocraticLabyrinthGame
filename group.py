import random

import game
from queue import Queue
import pygame
from dataclasses import dataclass
import tiles
import time


PLAYER_COLORS = [
    (255, 0, 0),
    (255, 97, 0),
    (255, 191, 0),
    (136, 255, 0),
    (0, 255, 4),
    (0, 255, 114),
    (0, 255, 237),
    (0, 127, 255),
    (0, 4, 255),
    (131, 0, 255),
    (255, 0, 255),
    (255, 0, 127),
    (255, 255, 255),
    (0, 0, 0)
]
random.shuffle(PLAYER_COLORS)


def color_to_hex(color: pygame.Color):
    result = "#"
    result += hex(color.r)[2:].capitalize()
    result += hex(color.g)[2:].capitalize()
    result += hex(color.b)[2:].capitalize()
    return result


@dataclass
class Direction:
    x: int = 0
    y: int = 0

    def as_single_int(self):
        if (self. x, self.y) == (0, 0):
            return None
        if (self. x, self.y) == (1, 0):
            return 0
        if (self. x, self.y) == (0, 1):
            return 1
        if (self. x, self.y) == (-1, 0):
            return 2
        if (self. x, self.y) == (0, -1):
            return 3

    @staticmethod
    def from_single_int_direction(direction):
        if direction is None:
            return Direction(0, 0)
        elif direction == 0:
            return Direction(1, 0)
        elif direction == 1:
            return Direction(0, 1)
        elif direction == 2:
            return Direction(-1, 0)
        elif direction == 3:
            return Direction(0, -1)


class Player:
    def __init__(self, settings, id, name):
        self.settings = settings

        self.id = id
        self.name = name

        self.squad = None

        self.goals = []
        self.knows_about = []
        self.direction = Direction()

        self.color = pygame.Color(*PLAYER_COLORS[id])

    def update_goals(self):
        for i, g in enumerate(self.goals):
            if g.update():
                del self.goals[i]

    def prepare_trap_minotaur_info(self):
        result = []
        p_pos_x, p_pos_y = self.squad.pos
        for trap in self.knows_about:
            horizontal_dif = p_pos_x - trap.pos_x
            vertical_dif = p_pos_y - trap.pos_y
            if 5 > abs(horizontal_dif) <= abs(vertical_dif):
                if horizontal_dif > 0:
                    result.append({"type": "trap", "pos": "right"})
                else:
                    result.append({"type": "trap", "pos": "left"})
            elif abs(vertical_dif < 5):
                if vertical_dif > 0:
                    result.append({"type": "trap", "pos": "up"})
                else:
                    result.append({"type": "trap", "pos": "down"})
        return result

    def to_dict(self):
        return {
            "name": self.name,
            "color": color_to_hex(self.color),
            "goals": [g.to_dict() for g in self.goals],
            "id": self.id,
            "pos_info": self.prepare_trap_minotaur_info()
        }


class Squad(pygame.sprite.Sprite):

    def __init__(self, settings, game_obj):
        super().__init__()

        self.settings = settings
        self.game: game.Game = game_obj
        self.player_list = []
        self.monuments = []

        self.equipment = {}
        # This might be necessary, but initializing dict entries is hopefully handled by TreasureTileGen
        # with open("treasurelist") as file:
        #     tresure_list = file.read().split('\n')
        # self.equipment = {t: 0 for t in tresure_list}

        self._pos_x = None
        self._pos_y = None

        self.direction = Direction()
        self.server_queue: Queue = None

        unscaled = pygame.image.load("assets/adventurer.png").convert_alpha()
        self.image = pygame.transform.scale(unscaled, (self.settings.tile_size, self.settings.tile_size))
        self.image.set_colorkey(settings.background_color)
        self.rect: pygame.Rect = self.image.get_rect()

        self.pos_x = 0
        self.pos_y = 0

    @property
    def pos(self):
        return self._pos_x, self.pos_y

    @pos.setter
    def pos(self, value):
        self.pos_x, self.pos_y = value

    @property
    def pos_x(self):
        return self._pos_x

    @pos_x.setter
    def pos_x(self, value):
        if value < 0:
            value = 0
        if value >= self.settings.width:
            value = self.settings.width - 1
        self._pos_x = value
        self.rect.x = value * self.settings.tile_size

    @property
    def pos_y(self):
        return self._pos_y

    @pos_y.setter
    def pos_y(self, value):
        if value < 0:
            value = 0
        if value >= self.settings.height:
            value = self.settings.height - 1
        self._pos_y = value
        self.rect.y = value * self.settings.tile_size

    def vote_direction(self):
        results = [0, 0, 0, 0]
        for player in self.player_list:
            if player.direction.as_single_int() is not None:
                results[player.direction.as_single_int()] += 1

        best_score = -1
        best_dir = None
        for i, score in enumerate(results):
            if score > best_score:
                best_dir = i
                best_score = score
            elif score == best_score:
                best_dir = None

        self.direction = Direction.from_single_int_direction(best_dir)

    def update_player_decisions(self):
        decisions = self.server_queue.get()
        for player in self.player_list:
            player.direction = Direction.from_single_int_direction(decisions[player.id])

    def make_decision_arrows(self, surf: pygame.Surface):
        def draw_arrow(start, end, color):
            pygame.draw.line(surf, color, start, end, self.settings.tile_size // 15)

        going_right_colors = []
        going_down_colors = []
        going_left_colors = []
        going_up_colors = []

        for player in self.player_list:
            if player.direction.as_single_int() == 0:
                going_right_colors.append(player.color)
            elif player.direction.as_single_int() == 1:
                going_down_colors.append(player.color)
            elif player.direction.as_single_int() == 2:
                going_left_colors.append(player.color)
            elif player.direction.as_single_int() == 3:
                going_up_colors.append(player.color)

        mid_x, mid_y = self.rect.center
        if going_right_colors:
            spacing = min(self.settings.tile_size // 6, self.settings.tile_size // len(going_right_colors))
            begin_y = mid_y - (spacing * len(going_right_colors) / 2)
            for i, color in enumerate(going_right_colors):
                start_x, _ = self.rect.midright
                start_y = begin_y + i * spacing
                draw_arrow((start_x, start_y), (start_x + self.settings.tile_size, start_y), color)

        if going_down_colors:
            spacing = min(5, self.settings.tile_size // len(going_down_colors))
            begin_x = mid_x - (spacing * len(going_down_colors) / 2)
            for i, color in enumerate(going_down_colors):
                _, start_y = self.rect.midbottom
                start_x = begin_x + i * spacing
                draw_arrow((start_x, start_y), (start_x, start_y + self.settings.tile_size), color)

        if going_left_colors:
            spacing = min(5, self.settings.tile_size // len(going_left_colors))
            begin_y = mid_y - (spacing * len(going_left_colors) / 2)
            for i, color in enumerate(going_left_colors):
                start_x, _ = self.rect.midleft
                start_y = begin_y + i * spacing
                draw_arrow((start_x, start_y), (start_x - self.settings.tile_size, start_y), color)

        if going_up_colors:
            spacing = min(5, self.settings.tile_size // len(going_up_colors))
            begin_x = mid_x - (spacing * len(going_up_colors) / 2)
            for i, color in enumerate(going_up_colors):
                _, start_y = self.rect.midtop
                start_x = begin_x + i * spacing
                draw_arrow((start_x, start_y), (start_x, start_y - self.settings.tile_size), color)

    def update(self, *args):
        for player in self.player_list:
            player.update_goals()
        self.update_player_decisions()
        self.vote_direction()

        if time.time() - self.game.last_minotaur_move > self.settings.move_time and self.game.last_minotaur_move > self.game.last_player_move:
            self.game.last_player_move = time.time()
            dest = (self.pos_x + self.direction.x, self.pos_y + self.direction.y)
            collision = bool(self.game.wall_graph.get(self.pos)) and dest in self.game.wall_graph.get(self.pos)
            if not collision:
                self.pos_x += self.direction.x
                self.pos_y += self.direction.y

                consumed = self.game.board[self.pos_y][self.pos_x].on_step(self)
                if consumed:
                    self.game.board[self.pos_y][self.pos_x].kill()
                    self.game.board[self.pos_y][self.pos_x] = tiles.Tile(self.settings, self.pos_x, self.pos_y)
