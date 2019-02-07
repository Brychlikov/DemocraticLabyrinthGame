import pygame
import time
from loguru import logger
import game


class Tile(pygame.sprite.Sprite):
    groups = []

    def __init__(self, settings, x, y):
        super().__init__(*Tile.groups)

        self.settings: game.Settings = settings
        self.image = pygame.Surface((settings.tile_size, settings.tile_size), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()

        self._pos_x = None
        self._pos_y = None

        self.pos_x = x
        self.pos_y = y

    def on_step(self, group):
        pass

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


class Treasure(Tile):
    def __init__(self, settings, x, y, name):
        super().__init__(settings, x, y)
        self.name = name

        unscaled = pygame.image.load("assets/treasure.png").convert_alpha()
        self.image = pygame.transform.scale(unscaled, (self.settings.tile_size, self.settings.tile_size))

    def on_step(self, group):
        group.equipment[self.name] += 1
        return True


class TrapTile(Tile):
    def __init__(self, settings, x, y):
        super().__init__(settings, x, y)

        self.players_knowing = []

    def add_aware_player(self, player):
        player.knows_about.append(self)


class StunTrap(TrapTile):
    def __init__(self, settings, x, y):
        super().__init__(settings, x, y)

    def on_step(self, group):
        logger.debug("Stepped on a stun trap")
        group.game.last_player_move = time.time() + 10


class LabExit(Tile):
    def __init__(self, settings, x, y):
        super().__init__(settings, x, y)

    def on_step(self, group):
        logger.debug("Labyrinth finished")
        group.game.labyrinth_finished = True


class Monument(Tile):
    def __init__(self, settings, x, y, name):
        super().__init__(settings, x, y)
        self.name = name

    def on_step(self, group):
        group.monuments.append(self.name)
