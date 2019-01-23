import pygame
import sys
from loguru import logger

logger.remove(0)
logger.add(sys.stdout, level="WARNING")

from game import Game, Settings

if __name__ == '__main__':

    settings = Settings(20, 30, 30)
    game = Game(settings)
    game.init()
    game.loop()
