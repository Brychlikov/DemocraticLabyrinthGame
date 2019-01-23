import game as game_module
import group


class Goal:
    def __init__(self, player, game):
        self.player: group.Player = player
        self.game: game_module.Game = game
        self.progress = 0
        self.aim = None

        self.achieved = False
        self.achievable = True
        self.description = """To jest opis pustego celu. Nie powinieneś tego widzieć"""

    def update(self) -> bool:
        pass

    def get_progress(self):
        return self.progress, self.aim


class OutOfLabyrinthGoalMoreThan(Goal):
    def __init__(self, player, game, more_than):
        super().__init__(player, game)
        self.description = f"Jesteś lingwistą (notabene słabo opłacanym). " \
                           f"Szukasz w labiryncie materiałów do badań na starożytną greką. " \
                           f"Zostań w labiryncie przez co najmniej {self.more_than} tur, " \
                           f"aby przepisać inskrypcje ze ścian. Może przy okazji znajdziesz jakieś zapomniajne dzieło literackie?"
        self.aim = 1
        self.more_than = more_than

    def update(self):
        if self.game.squad.equipment['HomerBook'] == 1:
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
        self.description = f"Nie każdy jest idealny, niektórzy nie radzą sobie w szkole, " \
                           f"inni nie mają przyjaciół, a ty masz klaustrofobię.  Wydostań się z labirynu w mniej niż {self.less_than} tur. "

    def update(self):
        if self.game.squad.equipment['NarcyzMirror'] == 1:
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
        self.description = f"znajdz {name} w liczbie {amount}"

    def update(self):
        if self.game.squad.equipment[self.name] == self.aim:
            print(f"gracz {self.player.name} znalazl odpowiednio duzo {self.name}")
            self.achieved = True
            return  True
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


