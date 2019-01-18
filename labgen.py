from dataclasses import dataclass


@dataclass
class Wall:
    x1: int = 0
    x2: int = 0
    y1: int = 0
    y2: int = 0
    passage_x: int = 0
    passage_y: int = 0


if __name__ == '__main__':
    w = Wall(0, 0, 0, 0, 0, 0, )
    print(w)
