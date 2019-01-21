import game
import group


class Goal:
    def __init__(self, player: group.Player, game_object):
        self.player = player
        self.game: game.Game = game_object
        self.progress = 0
        self.aim = None

        self.achieved = False
        self.achievable = True

        self.description = """To jest opis pustego celu. Nie powinieneś tego widzieć"""

    def update(self) -> bool:
        pass

    def get_progress(self):
        return self.progress, self.aim


class OutOfLabyrinthGoal(Goal):
    def __init__(self, player, game, less_than):
        super().__init__(player, game)

        self.aim = 1
        self.less_than = less_than

    def update(self):
        if self.game.labyrinth_finished and self.game.turns < self.less_than:
            self.achieved = True
            return True
        elif self.game.turns >= self.less_than:
            self.achievable = False
        return False


class GetTreasureGoal(Goal):
    def __init__(self,player, game_object, name,amount):
        super().__init__(player, game_object)

        self.aim=amount
        self.name = name

        self.description = f"znajdź {name} w liczbie {amount}"

    def update(self):
        if self.game.squad.equipment.get(self.name) == self.aim:
            print(f"gracz {self.player.name} osiągnął cel zdobycia {self.name}")
            self.achieved = True
            return True
        else:
            self.achievable = True


class PandoraTreasureGoal(Goal):
    def __init__(self,name):
        super().__init__()

    def update(self):
        if self.game.squad.equipment[name] == 1:
            self.achieved = False
        else:
            self.achievable = True


def random_goals():
    return [
        "obal kapitalistyczny rząd",
        "zdaj niemiecki na co najmniej 3",
        "przyjdz na poprawki z historii"
    ]
