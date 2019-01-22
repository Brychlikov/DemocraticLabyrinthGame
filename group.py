import game
from queue import Queue
import pygame
from dataclasses import dataclass


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

        self.goals = []
        self.server = None
        self.direction = Direction()

    def update_server_decision(self):
        pass


class Squad(pygame.sprite.Sprite):

    def __init__(self, settings):
        super().__init__()

        self.settings = settings
        self.player_list = []
        self.monuments = []

        with open("treasurelist") as file:
            tresure_list = file.read().split('\n')
        self.equipment = {t: 0 for t in tresure_list}
        self._pos_x = None
        self._pos_y = None

        self.direction = Direction()
        self.server_queue: Queue = None

        self.image = pygame.Surface([self.settings.tile_size, self.settings.tile_size])
        self.image.fill((0, 255, 100))
        self.rect = self.image.get_rect()

        self.pos_x = 0
        self.pos_y = 0

    @property
    def pos_x(self):
        return self._pos_x

    @pos_x.setter
    def pos_x(self, value):
        self._pos_x = value
        self.rect.x = value * self.settings.tile_size

    @property
    def pos_y(self):
        return self._pos_y

    @pos_y.setter
    def pos_y(self, value):
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

    def update(self, *args):
        self.update_player_decisions()
        self.vote_direction()


















