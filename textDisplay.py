import collections

import pygame


class TextDisplay:
    def __init__(self, size, font_name, font_size, background_color=(0, 0, 0), font_color=(255, 255, 255)):
        self.font = pygame.font.SysFont(font_name, font_size)
        self.bg = background_color
        self.color = font_color

        self.size = size

        self.line_height = self.font.get_linesize()
        self.max_lines = size[1] // self.line_height
        self._text_queue = collections.deque(maxlen=self.max_lines)

    def draw_queue(self):
        result = pygame.Surface(self.size)
        result.fill(self.bg)
        for i, el in enumerate(self._text_queue):
            text = self.font.render(el, True, self.color)
            result.blit(text, (0, i * self.line_height))

        return result

    def print(self, text):
        line = ""
        for word in text.split(" "):
            if self.font.size(line + " " + word)[0] > self.size[0]:
                self._text_queue.append(line)
                line = word + " "
            else:
                line += word + " "
        self._text_queue.append(line)

    def flush(self):
        self._text_queue = collections.deque(maxlen=self.max_lines)


if __name__ == '__main__':
    pygame.init()
    display: pygame.Surface = pygame.display.set_mode((500, 500))
    td = TextDisplay((500, 250), "helvetica", 20)
    clock = pygame.time.Clock()

    td.print("witam")
    td.print("bardzo bardzo bardzo bardzo bardzo bardzo  bardzo długi test")

    i = 0

    done = False
    while not done:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = True

        display.fill((255, 255, 255))
        display.blit(td.draw_queue(), (0, 0))

        td.print(str(i))
        i += 1


        pygame.display.flip()
        clock.tick(3)

    pygame.quit()

