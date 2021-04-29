from discord.ext import commands
from global_objs import Game
import discord
from global_objs import *

class Global_commands (commands.Cog, name="Global Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(lambda ctx: ctx.author.id in game_masters)
    async def set_pfp(self, ctx):
        """
        Changes the bot's profile picture
        
        Parameters:
        -----------
        pfp (as an attachment) - the picture to set as the bot's pfp
        """
        if len(ctx.message.attachments) < 1:
            await ctx.channel.send("Invalid attachment")
            return

        await ctx.message.attachments[0].save(fp="downloads/picture")

        with open("downloads/picture", "rb") as p:
            await self.bot.user.edit(avatar=p.read())

        await ctx.channel.send("Profile picture changed")
    
    @commands.command()
    async def game_status(self, ctx, *game_name):
        """
        Sends the progress of a specified game
        
        Parameters:
        -----------
        game name - the name of the game to check

        On Fail:
        --------
        Sends a list of names of the valid games
        """

        game_name = " ".join(game_name)
        try:
            game = Game.get_game(game_name)
        except KeyError:
            await ctx.channel.send("Invalid game. Please choose one of the following:\n```{}```".format("\n".join(Game.all_games())))
            return

        embed = discord.Embed(title=game_name.capitalize(), color=0x0000ff)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        if isinstance(game, list):
            for g in game:
                embed.add_field(name="Has started", value=g.begun)
                embed.add_field(name="Players", value="{}\n".format(", ".join([f"<@!{i}>" for i in g.players]) if len(g.players) >= 1 else "🕸️"), inline=False)
        else:
            embed.add_field(name="Has started", value=game.begun, inline=False)
            embed.add_field(name="Players", value="{}".format(", ".join([f"<@!{i}>" for i in game.players]) if len(game.players) >= 1 else "🕸️"))

        await ctx.channel.send(ctx.author.mention, embed=embed)
        