import pygame
import game


class Tile(pygame.sprite.Sprite):

    groups = []

    def __init__(self, settings, x, y):
        super().__init__(Tile.groups)

        # global settings object
        self.settings: game.Settings = settings

        # image of the tile. Black square by default
        self.image = pygame.Surface((settings.tile_size, settings.tile_size))

        # rect representing sprite's position on the screen
        self.rect = self.image.get_rect()

        self._pos_x = None
        self._pos_y = None

        # these represent tile's position in game coordinates
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


class Treasure(Tile):
    def __init__(self, settings, x, y, name):
        super().__init__(settings, x, y)

        self.image = pygame.Surface((settings.tile_size, settings.tile_size))
        self.image.fill((255, 255, 255))

        self.name = name

    def on_step(self, group):
        if group.equipment.get(self.name):
            group.equipment[self.name] += 1
        else:
            group.equipment[self.name] = 1
