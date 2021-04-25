from discord.ext import commands
import discord

class Game:
    games = {}
    def __init__(self, name, min_players=2, allow_mid_joins=False, single_game=True):
        self.name = name
        self.begun = False
        self.player_list = set()
        self.allow_mid_joins = allow_mid_joins
        self.min_players = min_players
        self.single_game = single_game

        if single_game:
            Game.games[self.name] = self
            return
        
        if self.name not in Game.games:
            Game.games[self.name] = [self]
        else:
            Game.games[self.name].append(self)

    @staticmethod
    def all_games():
        return [g.name for g in Game.games.keys()]
    
    @staticmethod
    def existing_games(game_name):
        return len(Game.games[game_name]) if isinstance(Game.games[game_name], list) else 1

    @staticmethod
    def get_game(name, index=0):
        g = Game.games[name]
        if isinstance(g, list):
            g = g[index]
        return g

    def add_player(self, player : discord.Member):
        if self.begun and not self.allow_mid_joins:
            raise IndexError
        self.player_list.add(player.id)
    
    def remove_player(self, player : discord.Member):
        self.player_list.remove(player.id)
        if len(self.player_list) == 1:
            return list(self.player_list)[0]
        elif len(self.player_list) < 1:
            return None
        return False

    def remove_player(self, player_id : int):
        self.player_list.remove(player_id)
        if len(self.player_list) == 1:
            return list(self.player_list)[0]
        elif len(self.player_list) < 1:
            return None
        return False

    def begin(self):
        if len(self.player_list) < self.min_players:
            raise ValueError
        self.begun = True
    
    def end(self):
        self.begun = False
        self.player_list = set()

get_user_id = lambda tag: int(tag.replace('<', '').replace('>', '').replace('@', '').replace('!', ''))

game_server = 834881633373913158
game_masters = (830760441209815090, 689148779948933181)
game_lord_role = 834909450451288064
