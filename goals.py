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


class OutOfLabyrinthGoalMoreThan(Goal):
    def __init__(self, player, game, more_than):
        super().__init__(player, game)

        self.aim = 1
        self.more_than = more_than

    def update(self):
        if group.equipment['HomerBook'] == 1:
            self.achieved = True
        elif self.game.labyrinth_finished and self.game.turns > self.more_than:
            self.achieved = True
            return True
        elif self.game.turns <= self.more_than:
            self.achievable = False
        return False


class OutOfLabyrinthGoalLessThan(Goal):
    def __init__(self, player, game, less_than):
        super().__init__(player, game)

        self.aim = 1
        self.less_than = less_than

    def update(self):
        if group.equipment['NarcyzMirror'] == 1:
            self.achieved = True
        elif self.game.labyrinth_finished and self.game.turns < self.less_than:
            self.achieved = True
            return True
        elif self.game.turns >= self.less_than:
            self.achievable = False
        return False


class GetTreasureGoal(Goal):
    def __init__(self, player, game, name, amount):
        super().__init__(player, game)
        self.name = name
        self.aim = amount
        game.squad.equipment[name] = 0

    def update(self):
        if group.equipment[self.name] == self.aim:
            self.achieved = True
        else:
            self.achievable = True


class PandoraTreasureGoal(Goal):
    def __init__(self, player, game):
        super().__init__(player, game)


    def update(self):
        if group.equipment['PandoraBox'] == 1:
            self.achieved = False
        else:
            self.achievable = True


class SeeAMonumentGoal (Goal):
    def __init__(self, player, game, name):
        super().__init__(player, game)
        self.name = name

    def update(self):
        if self.name in group.monuments:
            self.achieved = True


