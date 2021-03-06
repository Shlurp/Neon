from discord.ext import commands
import discord

class Game:
    games = {}
    max_num_games = 10      # Maximum number of games per game type
    def __init__(self, name, min_players=2, max_players=None, allow_mid_joins=False, single_game=True, can_remove=True):
        self.name = name
        self.begun = False
        self.players = set()
        self.allow_mid_joins = allow_mid_joins
        self.min_players = min_players
        self.max_players = max_players
        self.single_game = single_game
        self.can_remove = can_remove

        if single_game:
            Game.games[self.name] = self
            return
        
        if self.name not in Game.games:
            Game.games[self.name] = [self]
        else:
            if len(Game.games[self.name]) >= Game.max_num_games:
                raise IndexError
            Game.games[self.name].append(self)

    @staticmethod
    def all_games():
        return [g for g in Game.games.keys()]
    
    @staticmethod
    def existing_games(game_name):
        return len(Game.games[game_name]) if isinstance(Game.games[game_name], list) else 1

    @staticmethod
    def get_game(name):
        return Game.games[name]

    def add_player(self, player : discord.Member):
        """
        Adds a player to the game

        Parameters:
        -----------
        player - discord member object to add to player list

        Returns:
        --------
        True - maximum player count reached, causes game to start
        False - maximum player count not reached yet

        Throws:
        -------
        IndexError - cant add player to list (game has started)
        """

        if (self.max_players != None and len(self.players) >= self.max_players) or (self.begun and not self.allow_mid_joins):
            raise IndexError
        self.players.add(player.id)

        if len(self.players) == self.max_players:
            self.begin()
            return True

        return False
    
    def remove_player(self, player : discord.Member):
        self.players.remove(player.id)
        if len(self.players) == 1:
            return list(self.players)[0]
        elif len(self.players) < 1:
            return None
        return False

    def remove_player(self, player_id : int):
        self.players.remove(player_id)
        if len(self.players) == 1:
            return list(self.players)[0]
        elif len(self.players) < 1:
            return None
        return False

    def begin(self):
        if len(self.players) < self.min_players:
            raise ValueError
        self.begun = True
    
    def end(self):
        self.begun = False
        self.players = set()

    def get_player_tags(self):
        return [f"<@!{p_id}>" for p_id in self.players]

get_user_id = lambda tag: int(tag.replace('<', '').replace('>', '').replace('@', '').replace('!', ''))

game_server = 834881633373913158
game_masters = (830760441209815090, 689148779948933181)
game_lord_role = 834909450451288064

is_mod = lambda ctx: (isinstance(ctx.author, discord.Member) and (ctx.author.guild_permissions.administrator or discord.utils.get(ctx.author.roles, id=game_lord_role) != None)) or ctx.author.id in game_masters