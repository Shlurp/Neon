from discord.ext import commands
from dotenv import load_dotenv
from global_objs import *
import hunger_games_commands
import battleship_commands
import global_commands
import discord
import traceback
import sys
import os

game_bot = commands.Bot(command_prefix='!')
game_bot.add_cog(hunger_games_commands.HGgame_Cog(game_bot))
game_bot.add_cog(global_commands.Global_commands(game_bot))
game_bot.add_cog(battleship_commands.Battleship_Cog(game_bot))

load_dotenv()
game_bot.run(os.getenv("TOKEN"))

def get_diff(s1 : str, s2 : str) -> int:
    is1 = s1.lower()
    is2 = s2.lower()

    diff = 0
    for i in range(min(len(s1), len(s2))):
        diff += abs(ord(is1[i]) - ord(is2[i]))

    return diff

@game_bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass
    
    print(isinstance(error, commands.CommandNotFound))
    if isinstance(error, commands.CommandNotFound):
        cmd = ctx.invoked_with
        potentials = []
        for c in game_bot.commands:
            diff = get_diff(cmd, c.name)
            if len(potentials) < 3:
                potentials.append((c.name, diff))
            else:
                maxi = (0, potentials[0])
                i = 0
                for c, d in potentials:
                    if d > maxi[1]:
                        maxi = (i, d)
                    i += 1

                if diff < maxi[1]:
                    potentials.pop(maxi[0])
                    potentials.append((c.name, diff))

        await ctx.send("{} invalid command.\nDid you mean:\n{}".format(ctx.author.mention, "\n".join([p[0] for p in potentials])))
    