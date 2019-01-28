import game
import group


class Goal:
    def __init__(self, player: group.Player, game_obj):
        self.player = player
        self.game: game.Game = game_obj
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
        self.description = f"Jesteś lingwistą (notabene słabo opłacanym). " \
                           f"Szukasz w labiryncie materiałów do badań nad starożytną greką. " \
                           f"Zostań w labiryncie przez co najmniej {self.more_than} tur, " \
                           f"aby przepisać inskrypcje ze ścian. " \
                           f"Może przy okazji znajdziesz jakieś zapomniane dzieło literackie?"
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
        self.description = f"Nie każdy jest idealny, niektórzy nie radzą sobie w szkole, " \
                           f"inni nie mają przyjaciół, a ty masz klaustrofobię.  " \
                           f"Wydostań się z labiryntu w mniej niż {self.less_than} tur," \
                           f"zanim bedziesz musiał zmienić spodnie. " \
                           f"Gdyby tylko ktoś zostawił tu gdzieś lustro, które daje iluzję przestrzeni! "

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
        self.description = f"Ostatniej nocy przyśniła Ci się Afrodyta " \
                           f"i po starej znajomości powiedziała Ci o czym marzy Twoja druga połówka." \
                           f"Znajdź {name} a do końca życia będziecie szczęśliwi!"

    def update(self):
        if group.equipment[self.name] == self.aim:
            self.achieved = True
        else:
            self.achievable = True


class PandoraTreasureGoal(Goal):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.descriptions = f"Jeśli myślisz, że twoje życie wypełnione jest porażkami," \
                            f"świat jest dla ciebie okrutny i nie masz przyjaciół" \
                            f"Pomyśl o ile gorzej Ci będzie jeśli znajdzieesz Puszkę Pandory." \
                            f"Zaufaj mi, pod żadnym pozorem nie zbliżaj się do tej puszki!"

    def update(self):
        if group.equipment['PandoraBox'] == 1:
            self.achieved = False
        else:
            self.achievable = True


class SeeAMonumentGoal (Goal):
    def __init__(self, player, game, name):
        super().__init__(player, game)
        self.name = name
        self.description = f"Po wielu rodzinnych kłótniach mamusia puśicła Cię " \
                           f"na wycieczkę do labiryntu pod tym warunkiem, że wyślesz jej kilka zdjęć." \
                           f"Jako dobre dziecko musisz odnaleźć {name} i strzelić sobie z nim samojebkę"
    def update(self):
        if self.name in group.monuments:
            self.achieved = True


