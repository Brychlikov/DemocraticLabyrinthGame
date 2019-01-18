import pygame
from labgen import Wall
from tiles import Tile
from dataclasses import dataclass

@dataclass
class Settings:
    tile_size: int
    width: int
    height: int


class Board:
    def __init__(self, settings):
        self.board = [[Tile() for i in range(settings.width)] for j in range(settings.height)]


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.board = Board(settings)
