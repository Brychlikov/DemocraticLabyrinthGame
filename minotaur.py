import time
from loguru import logger

import pygame
import random
import game
import group
from collections import deque


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
    for x in range(settings.width):
        for y in range(settings.height):
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
        self.ticks = 0
        self.ticks_timer = False

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
            if (abs(self.pos_x - self.game.squad.pos_x) > 6 and abs(self.pos_y - self.game.squad.pos_y) > 6) or self.ticks_timer == True:
                logger.debug("SEARCHING")
                self.ticks += 1
                if self.ticks > 15:
                    self.ticks = 0
                    self.ticks_timer = False
                if time.time() - self.game.last_player_move > self.settings.move_time and self.game.last_player_move > self.game.last_minotaur_move:
                    possible = self.game.nrwg[self.pos]
                    dest = random.choice(possible)
                    self.pos_x = dest[0]
                    self.pos_y = dest[1]
                    self.game.last_minotaur_move = time.time()
            else:
                logger.debug("CHASING")
                self.ticks += 1
                if self.ticks > 15:
                    self.ticks = 0
                    self.ticks_timer = True
                queue = deque()
                queue.appendleft(self.pos)
                result = []
                came_from = []
                visited = set(self.pos)
                while len(queue) > 0:
                    node = queue.popleft()
                    if node == self.game.squad.pos:
                        break
                    for n in self.group.nrwg[node]:
                        if n not in visited:
                            visited.add(n)
                            queue.append(n)
                            came_from[n] = node
                next_node = came_from[self.game.squad.pos]
                while next_node != self.pos:
                    result.insert(0, next_node)
                    next_node = came_from[next_node]
                self.pos = result[0]

        if self.pos == self.game.squad.pos:
            if self.group.power / len(self.game.squad.player_list) > 5:
                self.kill()
            self.game.squad.dead = True


if __name__ == "__main__":
    settings = game.Settings(20, 30, 30)

    minotaur = Minotaur(settings)

    minotaur.pos_x = random.randrange(0, settings.width)
    minotaur.pos_y = random.randrange(0, settings.height)



