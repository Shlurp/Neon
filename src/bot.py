from discord.ext import commands
from dotenv import load_dotenv
from global_objs import *
import hunger_games_commands
import global_commands
import discord
import traceback
import sys
import os

game_bot = commands.Bot(command_prefix='!')
game_bot.add_cog(hunger_games_commands.HGgame_Cog(game_bot))
game_bot.add_cog(global_commands.Global_commands(game_bot))

load_dotenv()
game_bot.run(os.getenv("TOKEN"))

@game_bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        pass
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    