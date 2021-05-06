from discord.ext import commands
import discord
import misc.embeds as embeds

class HowTo_Cog(commands.Cog, name="How To"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def howto (self, ctx, *game):
        """
        Send instructions on how to play a game.

        Parameters:
        -----------
        game - the name of the game to send instructions for
        """
        
        game = " ".join(game).lower()
        files = {
            "hunger games" : "howto_hunger_games.txt",
            "battleship" : "howto_battleship.txt",
            "simon" : "howto_simon.txt"
        }
        
        if game not in files:
            await ctx.send("Invalid game. Try:\n ```{}```".format('\n'.join(files.keys())))
            return
        
        embed = embeds.get_embed(f"data/{files[game]}", ctx)
        await ctx.send(embed=embed)