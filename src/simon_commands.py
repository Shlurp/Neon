from global_objs import *
from discord.ext import commands
import discord
import random
import asyncio
from enum import Enum

class Arrow (Enum):
    up = "⬆️"
    down = "⬇️"
    left = "⬅️"
    right = "➡️"

class Simon_Cog(commands.Cog, name="Simon"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.id == 839539768748408872)
    async def simon(self, ctx):
        """
        Play Simon

        After the bot stops sending emojis, react with those emojis in the order they were sent
        """

        num_arrows = 1
        delay = 1
        Arrows = list(Arrow)

        message = await ctx.send("Get ready!")
        points = 0
        
        for j in range(10):
            arrows = [str(random.choice(Arrows).value) for i in range(num_arrows)]
            await asyncio.sleep(2)
            for i in arrows:
                await message.edit(content=i)
                await asyncio.sleep(delay)
                await message.edit(content=":black_large_square:")
                asyncio.sleep(0.1)
            await message.edit(content="Your turn! (Use reactions)")

            for i in arrows:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=lambda reac, user: user == ctx.author and reac.message == message, timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send("You timed out, but you had {} points!".format(points))
                    return

                if str(reaction.emoji) != i:
                    await ctx.send("Oh no! You made a mistake. You entered {}, when it should've been {}\nYou had {} points!".format(reaction, i, points))
                    return

                await message.clear_reactions()

            points += 1
            await message.edit(content="Nice job! You have {} points so far".format(points))
            delay /= 1.1
            num_arrows += 1

        await message.edit("Nice job! You've beat the game with {} points!".format(points))
