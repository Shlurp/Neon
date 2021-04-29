from hunger_games.actions import *
from global_objs import *
from discord.ext import commands
import discord

is_valid_player = lambda ctx: HGgame.begun and ctx.author.id in HGgame.player_list
is_mod = lambda ctx: (isinstance(ctx.author, discord.Member) and (ctx.author.guild_permissions.administrator or discord.utils.get(ctx.author.roles, id=game_lord_role) != None)) or ctx.author.id in game_masters  

class HGgame_Cog (commands.Cog, name="Hunger Games"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_mod)
    async def HGstart(self, ctx):
        """
        Starts the Hunger Games game

        Will only succeed if 2 or more people have joined
        """

        if HGgame.begun:
            await ctx.channel.send("Game has begun already")
            return

        try:
            HGgame.begin()
        except ValueError:
            await ctx.channel.send("Too few people")
            return

        await ctx.channel.send("Game has begun")

    @commands.command()
    async def HGjoin(self, ctx):
        """
        Adds caller to the queue for the hunger games game.

        Fails if game is already in progress
        """

        try:
            start = HGgame.add_player(ctx.author)
            await ctx.channel.send("Joined!")
            if start:
                await ctx.channel.send("{}\n**Hunger games: Game has started**".format("".join(HGgame.get_player_tags())))
        except IndexError:
            await ctx.channel.send("Game is already in progress")
            return

    @commands.command()
    @commands.check(is_valid_player)
    async def HGattack(self, ctx):
        """
        Attempts to attack another tribute in the same sector as you.

        The other tribute has a chance (albeit a smaller one) of beating you. 
        The weapon chosen to do damage is randomly selected from one of your inentories.
        """

        if False:
            try:
                victim_id = get_user_id(victim)
            except ValueError:
                await ctx.channel.send("Invalid target ID")
                return
            
            if str(victim_id) not in HGgame.tributes:
                await ctx.channel.send("Invalid target ID")
                return
        

        aggressor = HGgame.tributes[str(ctx.author.id)]

        state, attacker, victim, weapon = attack(aggressor)

        status = False
        if state == None:
            message = "There are no other tributes in your sector"
        elif state == 0:
            message = "During the fight, {} tried to kill {} with their {}, but didn't have enough stamina.".format(attacker, victim, weapon)
        elif state == 1:
            message = "During the fight, {} was able to wound {} with their {}".format(attacker, victim, weapon)
        else:
            message = "During the fight, {} killed {} with their {}".format(attacker, victim, weapon)
            status = HGgame.remove_player(int(victim.id))
            HGgame.remove_player_from_map(int(victim.id))

        await ctx.channel.send(message)

        if status != False:
            await ctx.channel.send("{} has won the game! Good game!".format(f"<@!{status}>" if status != None else "No one"))
            HGgame.end()

    @commands.command()
    @commands.check(is_valid_player)
    async def HGsearch(self, ctx):
        """
        Pick up a random in-game object

        Rarity/level of object is dependent on how close you are to the middle of the map
        """

        tribute = HGgame.tributes[str(ctx.author.id)]

        weapon = search(tribute)

        await ctx.channel.send("{} found {}".format(tribute, f"a {weapon}" if weapon != None else "nothing"))

    @commands.command()
    @commands.check(is_valid_player)
    async def HGdrop(self, ctx, weapon_name):
        """
        Drops an item from your inventory.

        You can only drop items that are in your inventory.

        Parameters:
        -----------
        weapon name - the name of the weapon to drop
        """

        tribute = HGgame.tributes[str(ctx.author.id)]

        try:
            if tribute.remove_weapon(weapon_name) == True:
                await ctx.channel.send("{} dropped a {}".format(tribute, weapon_name))
            else:
                await ctx.channel.send("{} attempted to drop a {}, but had none.".format(tribute, weapon_name))
        except IndexError:
            await ctx.channel.send("{} not enough weapons".format(tribute))
        except ValueError:
            await ctx.channel.send("{} have you ever tried dropping your fists?".format(tribute))
        

    @commands.command()
    @commands.check(is_valid_player)
    async def HGme(self, ctx):
        """
        Sends your in-game status
        """

        tribute = HGgame.tributes[str(ctx.author.id)]

        embed = discord.Embed(title=ctx.author.display_name, color=0xff0000)
        embed.set_thumbnail(url=ctx.author.avatar_url)

        embed.add_field(name="Health", value=tribute.health)
        embed.add_field(name="Stamina", value=tribute.stamina)

        inventory = "\n".join([str(i) for i in tribute.inventory])
        embed.add_field(name="Inventory", value=inventory if len(inventory) > 1 else "🕸️", inline=False)

        weapons = "\n".join([str(i) for i in tribute.weapons])
        embed.add_field(name="Weapons", value=weapons, inline=False)

        await ctx.channel.send(tribute, embed=embed)

    @commands.command()
    #@commands.check(is_valid_player)
    async def HGcheck(self, ctx, *object_name):
        """
        Sends information on an in-game object

        Parameters:
        -----------
        weapon name - the name of the weapon to check
        """

        object_name = " ".join(object_name).lower()

        for i in Items.items:
            if i.name == object_name:
                item = i
                break
        
        if item == None:
            await ctx.channel.send("Invalid object name")
            return

        embed = discord.Embed(title=object_name.capitalize(), color=0xff0000)
        if isinstance(item, Weapon):
            embed.add_field(name="Damage", value=item.damage)
            embed.add_field(name="Exertion", value=item.exertion)
        else:
            embed.add_field(name="Effect", value=item.effect.__doc__, inline=False)
            for key, value in item.data.items():
                embed.add_field(name=key.capitalize(), value=value)
        embed.add_field(name="Rarity", value=item.rarity)

        await ctx.channel.send(ctx.author.mention, embed=embed)
        return

    @commands.command()
    @commands.check(is_valid_player)
    async def HGmap(self, ctx):
        """
        Sends a map representing the danger levels (the number of tributes) in each sector. 

        Also sends your coordinates (relative to the top left corner)
        The circle is where you are.
        """

        tribute = HGgame.tributes[str(ctx.author.id)]

        dmap = get_danger_map(tribute.x, tribute.y)

        await ctx.channel.send("({}, {})\n\n{}".format(tribute.x, tribute.y, "\n".join(["".join(i) for i in dmap])))

    @commands.command()
    @commands.check(is_valid_player)
    async def HGmove(self, ctx, direction : str):
        """
        Moves you in a certain direction

        Parameters:
        -----------
        direction - the direction you want to move in (left, right, up, or down)
        """

        movements = {"left" : (-1, 0), "right" : (1, 0), "up" : (0, -1), "down" : (0, 1)}
        direction = direction.lower()

        if direction not in movements:
            await ctx.channel.send("{} Invalid direction ({})".format(ctx.author.mention, ", ".join(movements.keys())))
            return
        
        c = movements[direction]

        try:
            HGgame.move_player(ctx.author.id, c[0], c[1])
            await ctx.channel.send("{} moved!".format(ctx.author.mention))
        except IndexError:
            await ctx.channel.send("{} Invalid movement".format(ctx.author.mention))
            return

    @commands.command()
    @commands.check(is_valid_player)
    async def HGuse(self, ctx, *obj):
        """
        Use an in-game object

        Parameters:
        -----------
        obj - the name of the object to use
        """

        tribute = HGgame.tributes[str(ctx.author.id)]
        obj_name = " ".join(obj)
        i = 0

        while i < len(tribute.inventory):
            if tribute.inventory[i].name == obj_name:
                break
            i += 1

        if i == len(tribute.inventory):
            await ctx.channel.send("Invalid object")
            return
        
        item = tribute.inventory[i]
        item.call(tribute)
        tribute.inventory.pop(i)

        await ctx.channel.send("{} used their {}".format(tribute, obj_name))

    @commands.command()
    @commands.check(is_valid_player)
    async def HGweary(self, ctx):
        """
        Wear yourself down (for testing purposes, or if you're a sore loser)
        """
        
        tribute = HGgame.tributes[str(ctx.author.id)]

        tribute.health = tribute.health - 1 if tribute.health > 1 else tribute.health
        tribute.stamina = tribute.stamina - 1 if tribute.stamina > 1 else tribute.stamina

        await ctx.channel.send("{} got wearier".format(tribute))
