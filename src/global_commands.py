from discord.ext import commands
from global_objs import Game, is_mod
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

    @commands.command()
    @commands.check(is_mod)
    async def dropout(self, ctx, member : discord.Member, *options):
        """
        Remove a player from a game

        Parameters:
        -----------
        member - the member to remove
        game - the name of the game
        
        Flags:
        ------
        -r - recursive flag - search over list of games and remove member (if there are multiple games in progress)
        -f - force flag - force remove member even if game has started
        """
        
        game = ""
        for s in options:
            if s[0] != '-':
                game += s.lower()

        if game not in Game.games:
            await ctx.send("Invalid game!")
            return

        if type(Game.games[game]) == list:
            if '-r' not in options:
                await ctx.send("Invalid game type (list detected, use -r to dropout)")
                return
            
            found = False
            force = '-f' in options

            for g in Game.games[game]:
                if g.can_remove and member.id in g.players and (not g.begun or force):
                    Game.games[game].players.remove(member.id)
                    found = True
                    break
            if not found:
                await ctx.send("Invalid member / can't remove member!")
                return
        
        else:
            if member.id not in Game.games[game].players:
                await ctx.send("Invalid member!")
                return
            if not Game.games[game].can_remove or (g.begun and not force):
                await ctx.send("Can't remove member")
                return
            Game.games[game].players.remove(member.id)
        await ctx.send("Member **{}** removed from game **{}**".format(member.display_name, game.capitalize()))
            
        