import time
from loguru import logger

import pygame
import random
import game
import group


def neighbours(x, y, settings):
    result = set()
    if x - 1 >= 0:
        result.add((x-1, y))
    if x + 1 < settings.width:
        result.add((x + 1, y))
    if y - 1 >= 0:
        result.add((x, y-1))
    if y + 1 < settings.height:
        result.add((x, y + 1))
    return result


def non_retarded_wall_graph(wall_graph, settings):
    result = {}
    for x, y in zip(range(settings.width), range(settings.height)):
        result[(x, y)] = []
        for n in neighbours(x, y, settings):
            if wall_graph.get((x, y)) and n in wall_graph[(x, y)]:
                continue
            result[(x, y)].append(n)
    return result


class Minotaur(pygame.sprite.Sprite):
    groups = []

    def __init__(self, settings, game_obj):
        super().__init__(*Minotaur.groups)

        self.game: game.Game = game_obj
        self.settings: game.Settings = settings
        unscaled = pygame.image.load("assets/Minotaur.png").convert_alpha()
        self.image = pygame.transform.scale(unscaled, (self.settings.tile_size, self.settings.tile_size))
        self.rect = self.image.get_rect()

        self._pos_x = None
        self._pos_y = None

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

    @property
    def pos(self):
        return self._pos_x, self._pos_y

    @pos.setter
    def pos(self, value):
        self.pos_x, self.pos_y = value

    def update(self):
        if time.time() - self.game.last_player_move > self.settings.move_time and self.game.last_player_move > self.game.last_minotaur_move:
            random_destination = group.Direction.from_single_int_direction(random.randint(0, 3))
            dest = (self.pos_x + random_destination.x, self.pos_y + random_destination.y)
            collision = bool(self.game.wall_graph.get(self.pos)) and dest in self.game.wall_graph.get(self.pos)
            if not collision:
                self.pos_x += random_destination.x
                self.pos_y += random_destination.y
            else:
                logger.warning("Minotaur hit a wall")
            self.game.last_minotaur_move = time.time()


if __name__ == "__main__":
    settings = game.Settings(20, 30, 30)

    minotaur = Minotaur(settings)

    minotaur.pos_x = random.randrange(0, settings.width)
    minotaur.pos_y = random.randrange(0, settings.height)



