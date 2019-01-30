import pygame


def make_background(surf: pygame.Surface, resolution):
    result = pygame.Surface(resolution)
    x, y = surf.get_size()
    for i in range(0, resolution[0], x):
        for j in range(0, resolution[1], y):
            result.blit(surf, (i, j))
    return result


if __name__ == '__main__':
    s = pygame.image.load("assets/tile.png")

    res = make_background(s, (1000, 500))
    pygame.image.save(res, "testbackground.png")
