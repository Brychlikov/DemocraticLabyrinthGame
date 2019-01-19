import pygame
import game


class Tile(pygame.sprite.Sprite):

    def __init__(self, settings, x, y):
        super().__init__()

        self.settings: game.Settings = settings
        self.image = pygame.Surface((settings.tile_size, settings.tile_size))
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
