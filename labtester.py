import pygame
from new_temp import actually_gen_lab

COLORS = [
    (0, 0, 255),
    (0, 100, 255),
    (0, 100, 100),
    (0, 255, 100),
    (0, 255, 0),
    (100, 255, 0),
    (100, 100, 0),
    (255,  100, 0),
    (255, 0, 0),
    (255, 255, 255),
    (100, 100, 100),
    (100, 0, 100),
    (255, 0, 255)
]

SHOW_DEPTH = False

tile_size = 30
lab_size = 12
wall_list = actually_gen_lab(10)

display = pygame.display.set_mode((tile_size * lab_size, tile_size * lab_size))
pygame.display.set_caption("Wielki generator labiryntów wielkiego i groźniego bazeli")

done = False
clock = pygame.time.Clock()
while not done:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done = True

    display.fill((0, 0, 0))
    wall_list = actually_gen_lab(10)
    for w in wall_list:
        if SHOW_DEPTH:
            pygame.draw.line(display, COLORS[w.depth], (w.x1 * tile_size, w.y1 * tile_size), (w.x2 * tile_size, w.y2 * tile_size), 3)
        else:
            pygame.draw.line(display, (0, 0, 255), (w.x1 * tile_size, w.y1 * tile_size), (w.x2 * tile_size, w.y2 * tile_size), 3)

    pygame.display.flip()

    clock.tick(0.3)

pygame.quit()
