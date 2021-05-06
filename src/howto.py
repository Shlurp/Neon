from discord.ext import commands
import discord
import misc.embeds as embeds

class HowTo_Cog(commands.Cog, name="How To"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def battleship(self, ctx):
        embed = embeds.get_embed("data/howto_battleship.txt", ctx)
        await ctx.send(embed=embed)
        