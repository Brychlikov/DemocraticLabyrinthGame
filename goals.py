import game as game_module
import group


class Goal:
    def __init__(self, player: group.Player, game: game_module.Game):
        self.player = player
        self.game = game
        self.progress = 0
        self.aim = None

        self.achieved = False
        self.achievable = True

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


def random_goals():
    return [
        "obal kapitalistyczny rząd",
        "zdaj niemiecki na co najmniej 3"
        "przyjdz na poprawki z historii"
    ]
