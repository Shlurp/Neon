from discord.ext import commands
from math import sqrt

class Error_Cog(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.letters = {}

        self.get_letters("data/keys.txt")
    
    def get_letters(self, filepath):
        """
        Enter letters into dict by (column, row)
        """

        with open(filepath, "r") as fp:
            y = 0
            for line in fp:
                x = 0
                for c in line:
                    self.letters[c] = (x, y)
                    x += 1
                y += 1

    def get_diff(self, s1 : str, s2 : str) -> float:
        """
        Calculate sum of distances between the characters in two strings (case insensitive)
        """

        is1 = s1.lower()
        is2 = s2.lower()

        diff = 0
        for i in range(min(len(is1), len(is2))):
            diff += sqrt((self.letters[is1[i]][0] - self.letters[is2[i]][0]) ** 2 + (self.letters[is1[i]][1] - self.letters[is2[i]][1]) ** 2)

        return diff


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass
        
        if isinstance(error, commands.CommandNotFound):
            cmd = ctx.invoked_with
            potentials = []
            for c in self.bot.commands:
                can_do = True
                for check in c.checks:
                    if not check(ctx):
                        can_do = False
                        break
                
                diff = self.get_diff(cmd, c.name) + (1 - can_do) * 2
                if len(potentials) < 3:
                    potentials.append((c.name, diff, can_do))
                else:
                    maxi = (0, -1)
                    i = 0
                    for _, difference, _ in potentials:
                        if difference > maxi[1]:
                            maxi = (i, difference)
                        i += 1

                    if diff < maxi[1]:
                        potentials.pop(maxi[0])
                        potentials.append((c.name, diff, can_do))

            await ctx.send("{} invalid command.\nDid you mean:\n{}\n".format(ctx.author.mention, "\n".join([f"`{p[0]}`" if p[2] else f"~~`{p[0]}`~~" for p in potentials])))