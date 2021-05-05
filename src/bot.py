from discord.ext import commands
from dotenv import load_dotenv
from global_objs import *
import hunger_games_commands
import battleship_commands
import global_commands
import error_cog
import howto
import discord
import traceback
import sys
import os

game_bot = commands.Bot(command_prefix='!')
game_bot.add_cog(hunger_games_commands.HGgame_Cog(game_bot))
game_bot.add_cog(global_commands.Global_commands(game_bot))
game_bot.add_cog(battleship_commands.Battleship_Cog(game_bot))
game_bot.add_cog(error_cog.Error_Cog(game_bot))
game_bot.add_cog(howto.HowTo_Cog(game_bot))

load_dotenv()
game_bot.run(os.getenv("TOKEN"))
    