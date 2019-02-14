from dataclasses import dataclass
import random
import time
random.seed(time.time())

DEBUG_NO_WALLS = False


@dataclass
class Chamber:
    upX: int = 0
    upY: int = 0
    downX: int = 0
    downY: int = 0


@dataclass
class Wall:
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    depth: int = 0


def build_lab(chamber, width, height, current_depth, max_depth):
    """
    Recursive way of generating a labyrinth:
    1. Start with an empty chamber. Add it to the list of chambers.
    2. Split the chamber, add new chambers to the list of chambers
    3. Create walls between split chambers.
    4. Recursively call this function with new made chambers.
    """
    result = []
    if width < 2 or height < 2 or current_depth == max_depth:
        return result #Stops recursion if the given chamber can't be split anymore/number of recursions hit the maximum.

    if current_depth == 0:
        """Adds outer walls to the labyrinth"""
        for i in range(chamber.downY):
            new_outer_wall = Wall()
            new_outer_wall.x1 = 0
            new_outer_wall.x1 = 0
            new_outer_wall.y1 = i
            new_outer_wall.y2 = i + 1
            result.append(new_outer_wall)
        for i in range(chamber.downY):
            new_outer_wall = Wall()
            new_outer_wall.x1 = chamber.downX
            new_outer_wall.x2 = chamber.downX
            new_outer_wall.y1 = i
            new_outer_wall.y2 = i + 1
            result.append(new_outer_wall)
        for i in range(chamber.downX):
            new_outer_wall = Wall()
            new_outer_wall.x1 = i
            new_outer_wall.x2 = i + 1
            new_outer_wall.y1 = 0
            new_outer_wall.y2 = 0
            result.append(new_outer_wall)
        for i in range(chamber.downX):
            new_outer_wall = Wall()
            new_outer_wall.x1 = i
            new_outer_wall.x2 = i + 1
            new_outer_wall.y1 = chamber.downX
            new_outer_wall.y2 = chamber.downX
            result.append(new_outer_wall)

        """
        Randomly pick coordinates of lab entrance and exit, 
        delete walls on those coordinates and return the list with outer walls and entrance/exit coords.
        """
        rand_exit = random.randrange(0, chamber.downX)
        entrance = result[rand_exit]
        exit = result[rand_exit + chamber.downX]
        del result[rand_exit]
        del result[rand_exit + chamber.downX - 1]

        if DEBUG_NO_WALLS:
            return result, entrance, exit

    orientation = orientation_changer(width, height)

    if orientation:
        """
        Splits a given chamber horizontally:
        1. Randomly pick Y-coordinate of a chamber. (rand_y)
        2. Cut the chamber through the given Y-coordinate.
        3. Add new chambers to the list of chambers.
        4. Randomly generate X-coordinate of an passage
        5. Generate walls at the given Y-coordinate but generate passage at a given X-coordinate.
        """
        rand_y = random.randrange(chamber.upY + 1, chamber.downY)
        passage_x = random.randrange(chamber.upX, chamber.downX)
        for i in range(chamber.upX, chamber.downX):
            if i == passage_x:
                continue #skips the iteration and makes a hole in a generated wall.
            new_wall_x = Wall()
            new_wall_x.x1 = i
            new_wall_x.x2 = i + 1
            new_wall_x.y1 = rand_y
            new_wall_x.y2 = rand_y
            new_wall_x.depth = current_depth
            result.append(new_wall_x)

        new_chamber_up = Chamber() #Create a new chamber.
        new_chamber_up.upX = chamber.upX
        new_chamber_up.downX = chamber.downX
        new_chamber_up.upY = chamber.upY
        new_chamber_up.downY = rand_y

        new_chamber_up_width = new_chamber_up.downX - new_chamber_up.upX
        new_chamber_up_height = new_chamber_up.downY - new_chamber_up.upY

        result.extend(build_lab(new_chamber_up, new_chamber_up_width, new_chamber_up_height, current_depth + 1, max_depth)) #Recursively call the same function with new chamber.

        new_chamber_down = Chamber() #Create a new chamber.
        new_chamber_down.upX = chamber.upX
        new_chamber_down.downX = chamber.downX
        new_chamber_down.upY = rand_y
        new_chamber_down.downY = chamber.downY

        new_chamber_down_width = new_chamber_down.downX - new_chamber_down.upX
        new_chamber_down_height = new_chamber_down.downY - new_chamber_down.upY

        result.extend(build_lab(new_chamber_down, new_chamber_down_width, new_chamber_down_height, current_depth + 1, max_depth)) #Recursively call the same function with new chamber.

    if not orientation:
        """
        Splits a given chamber vertically.
        The method is the same but instead it randomly picks X-coordinate and cuts the chamber through it.
        Randomly picks passage_y and makes a hole at it.
        """
        rand_x = random.randrange(chamber.upX + 1, chamber.downX)
        passage_y = random.randrange(chamber.upY, chamber.downY)
        for i in range(chamber.upY, chamber.downY):
            if i == passage_y:
                continue
            new_wall_y = Wall()
            new_wall_y.x1 = rand_x
            new_wall_y.x2 = rand_x
            new_wall_y.y1 = i
            new_wall_y.y2 = i + 1
            new_wall_y.depth = current_depth
            result.append(new_wall_y)

        new_chamber_left = Chamber()
        new_chamber_left.upX = chamber.upX
        new_chamber_left.downX = rand_x
        new_chamber_left.upY = chamber.upY
        new_chamber_left.downY = chamber.downY

        new_chamber_left_width = new_chamber_left.downX - new_chamber_left.upX
        new_chamber_left_height = new_chamber_left.downY - new_chamber_left.upY

        result.extend(build_lab(new_chamber_left,  new_chamber_left_width, new_chamber_left_height, current_depth + 1, max_depth))

        new_chamber_right = Chamber()
        new_chamber_right.upX = rand_x
        new_chamber_right.downX = chamber.downX
        new_chamber_right.upY = chamber.upY
        new_chamber_right.downY = chamber.downY

        new_chamber_right_width = new_chamber_right.downX - new_chamber_right.upX
        new_chamber_right_height = new_chamber_right.downY - new_chamber_right.upY

        result.extend(build_lab(new_chamber_right, new_chamber_right_width, new_chamber_right_height, current_depth + 1, max_depth))

    if current_depth == 0:
        return result, entrance, exit
    else:
        return result


def orientation_changer(width, height):
    """
    Function which decides whether the chamber should be split horizontally or vertically.
    If width is greater than height shall it be split vertically
    If height is greater than width it shall be split horizontally
    :param width: Width of a given chamber
    :param height:  Height of a given chamber
    :return:
    """
    if width < height:
        return True
    elif height < width:
        return False
    else:
        return random.choice([True, False])


def actually_gen_lab(lab_size):
    """Executes build_lab and returns list of walls"""
    first = Chamber() #The first chamber which will be continously split until the labyrinth is made.
    first.upX = 0
    first.upY = 0
    first.downX = lab_size
    first.downY = lab_size
    width = lab_size
    height = lab_size

    walls = build_lab(first, width, height, 0, 20)

    return walls

if __name__ == "__main__":
    lab_size = int(input("Lab size: "))
    print(actually_gen_lab(lab_size))
