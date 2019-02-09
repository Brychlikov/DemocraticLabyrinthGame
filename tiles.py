import random

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
        group.game.text_display.print(f"Odnaleźliście skarb - {self.name}!")
        group.equipment[self.name] += 1
        return True


class Weapon(Tile):
    def __init__(self, settings, x, y):
        super(Weapon, self).__init__(settings, x, y)

        unscaled = pygame.image.load("assets/treasure.png").convert_alpha()
        self.image = pygame.transform.scale(unscaled, (self.settings.tile_size, self.settings.tile_size))

    def on_step(self, group):
        group.game.text_display.print("Podnieśliście broń!")
        for p in group.player_list:
            if not random.randrange(0, 3):  # 25% chance of getting weapon for every player
                p.power += random.randint(1, 4)


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
        group.game.text_display.print("Wpadliście w pułapkę ogłuszającą!")
        group.stunned += 5
        return True


class VisionTrap(TrapTile):
    def __init__(self, settings, x, y):
        super(VisionTrap, self).__init__(settings, x, y)

    def on_step(self, group):
        logger.debug("Stepped on a vision trap")
        group.game.text_display.print("Wpadliście w pułapkę oślepiającą!")
        group.vision_radius //= 3
        group.impaired_vision_turns = 10
        return True



class LabExit(Tile):
    def __init__(self, settings, x, y):
        super().__init__(settings, x, y)

    def on_step(self, group):
        logger.debug("Labyrinth finished")
        group.game.text_display.print(f"Wyszliście z labiryntu w {self.game.turns} tur!")
        group.game.labyrinth_finished = True


class Monument(Tile):
    def __init__(self, settings, x, y, name):
        super().__init__(settings, x, y)
        self.name = name

    def on_step(self, group):
        group.monuments.append(self.name)
