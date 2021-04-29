from global_objs import *

class Ship:
    # ships = {"carrier" : 5, "battleship" : 4, "cruiser" : 3, "submarine" : 3, "destroyer" : 2}
    ships = {"carrier" : 2}

    def __init__(self, name, x1, y1, direction):
        self.name = name.lower()
        self.length = Ship.ships[name.lower()]

        if direction == "left":
            self.points = [(x1 - i, y1) for i in range(self.length)]
        elif direction == "right":
            self.points = [(x1 + i, y1) for i in range(self.length)]
        elif direction == "up":
            self.points = [(x1, y1 - i) for i in range(self.length)]
        elif direction == "down":
            self.points = [(x1, y1 + i) for i in range(self.length)]
        else:
            raise ValueError

        self.targets = [False for i in range(self.length)]

    def __len__(self):
        return self.length

    def __str__(self):
        return self.name

    def get_extremes(self):
        return (self.points[0], self.points[self.length - 1])

    def hit(self, index):
        if self.targets[index]:
            raise ValueError

        self.targets[index] = True

    def is_sunk(self):
        return False not in self.targets

class Board:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.board = [[(None, None) for i in range(width)] for j in range(height)]     # Board spots are set like so:
                                                                                        # Initialized to (None, None)
                                                                                        # Once a boat is set there, (Boat index, Boat spot index)
                                                                                        # Once fired on, if hit: (True, None)
                                                                                        # if miss: (False, None)
        self.boats = []
        self.ready = False

    def add_ship(self, s : Ship):
        if self.ready:
            raise ValueError
        if s.name in [b.name for b in self.boats]:
            raise NameError

        e = s.get_extremes()

        if not ((0 <= e[0][0] and e[0][0] < self.width) and (0 <= e[0][1] and e[0][1] < self.height) and
                (0 <= e[1][0] and e[1][0] < self.width) and (0 <= e[1][1] and e[1][1] < self.height)):
            raise IndexError

        for p in s.points:
            if self.board[p[1]][p[0]] != (None, None):
                raise ValueError

        i = 0
        for p in s.points:
            self.board[p[1]][p[0]] = (len(self.boats), i)       # Boat index, target index
            i += 1
        
        self.boats.append(s)
        if len(self.boats) == len(Ship.ships):
            self.ready = True
            return True
        return False
    
    def fire(self, x, y):
        boat_i, target_i = self.board[y][x]
        if not isinstance(boat_i, bool) and boat_i != None:    # Boat is located here, not hit
            self.boats[boat_i].hit(target_i)
            self.board[y][x] = (True, None)
            hit = True
        elif isinstance(boat_i, bool):                        # Already hit
            raise ValueError
        else:                               # Not hit, no boat
            self.board[y][x] = (False, None)
            hit = False

        return (hit, self.dead())

    def dead(self):
        for boat in self.boats:
            if not boat.is_sunk():
                return False

        return True

class BattleshipGame(Game):
    def __init__(self):
        self.boards = {}
        self.turn = 0
        self.players = []
        self.fighting = False
        super().__init__("battleship", single_game=False, max_players=2, min_players=2)

    def add_player(self, player):
        self.boards[str(player.id)] = Board()
        self.players.append(player.id)

        return super().add_player(player)

    def next_turn(self):
        self.turn = (self.turn + 1) % 2

    def begin_fight(self):
        if len(self.boards) != self.max_players:
            return False
    
        for b in self.boards.values():
            if not b.ready:
                return False
        
        self.fighting = True
        return True
