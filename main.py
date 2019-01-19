import pygame
from game import Game, Settings

if __name__ == '__main__':
    settings = Settings(20, 30, 30)
    game = Game(settings)
    game.init()
    game.loop()
