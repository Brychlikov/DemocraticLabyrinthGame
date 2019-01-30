import pygame
import random
import game
import group


class Minotaur(pygame.sprite.Sprite):
    groups = []

    def __init__(self, settings, game_obj):
        super().__init__(*Minotaur.groups)

        self.game: game.Game = game_obj
        self.settings: game.Settings = settings
        self.image = pygame.Surface((settings.tile_size, settings.tile_size), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
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
        self.game.wall_graph.get(self.pos)
        random_destination = group.Direction.from_single_int_direction(random.randint(0, 3))
        dest = (self.pos_x + random_destination.x, self.pos_y + random_destination.y)
        collision = bool(self.game.wall_graph.get(self.pos)) and dest in self.game.wall_graph.get(self.pos)
        if not collision:
            self.pos_x += random_destination.x
            self.pos_y += random_destination.y


if __name__ == "__main__":
    settings = game.Settings(20, 30, 30)

    minotaur = Minotaur(settings)

    minotaur.pos_x = random.randrange(0, settings.width)
    minotaur.pos_y = random.randrange(0, settings.height)


