from battleship.battleship_objs import *
import discord
from discord.ext import commands

def get_game(p_id) -> BattleshipGame:
    battleships = Game.games["battleship"]

    for b in battleships:
        if int(p_id) in b.players:
            return b

    return None

def is_valid_player(p_id):
    try:
        if get_game(p_id) != None:
            return True
        else:
            return False
    except KeyError:
        return False

def is_players_turn(p_id):
    try:
        b = get_game(p_id)
        if b != None:
            return b.player_list[b.turn] == int(p_id) and b.fighting
        else:
            return False
    except KeyError:
        return False

def is_fighting(p_id):
    try:
        b = get_game(p_id)
        if b != None:
            return b.fighting
        else:
            return False
    except KeyError:
        return False
    
is_valid_and_private = lambda ctx: ctx.channel.type == discord.ChannelType.private and is_valid_player(ctx.author.id)

class Battleship_Cog (commands.Cog, name="Battleship"):
    """
    Commands for the battleship game
    """
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.id == 839539754214752287 and not is_valid_player(ctx.author.id))
    async def BSjoin(self, ctx):
        """
        Adds you to a battleship game

        If one is available, you will join it, if not, one will be created.
        """

        try:
            last_game = Game.games["battleship"][-1]
        except KeyError:
            last_game = None

        if last_game == None or len(last_game.players) >= last_game.max_players:
            try:
                bsGame = BattleshipGame()
            except IndexError:
                await ctx.channel.send("{} too many games at the moment".format(ctx.author.mention))
                return
            bsGame.add_player(ctx.author)
            await ctx.channel.send("Joined!")
        else:
            if last_game.add_player(ctx.author):
                await ctx.channel.send("Joined!\n{}\n\n**Battleship: Game has started**".format("".join(last_game.get_player_tags())))
            else:
                await ctx.channel.send("An unexpected situation occurred, please report this.")
    
    @commands.command()
    @commands.check(lambda ctx: is_valid_and_private(ctx) and not is_fighting(ctx.author.id))
    async def BSset(self, ctx, shipname : str, direction : str, x0 : int, y0 : int):
        """
        Place a ship on your board

        This can only be used before the fighting stage of the game begins (when the last ship is placed)

        Parameters:
        -----------
        shipname - the name of the ship to place, must be one of the following: carrier, battleship, cruiser, submarine, destroyer
        direction - orientation of the ship - left, right, down, up
        x0 - starting x position (0 - left, 9 - right)
        y0 - starting y position (0 - top, 9 - bottom)
        """

        try:
            ship = Ship(shipname.lower(), x0, y0, direction.lower())
        except KeyError:
            await ctx.channel.send("{} invalid ship name.\nChoose one of the following:\n{}".format(ctx.author.mention, ", ".join([s.capitalize() for s in Ship.ships])))
            return
        except ValueError:
            await ctx.channel.send("{} invalid direction".format(ctx.author.mention))
            return

        game = get_game(ctx.author.id)
        try:
            game.boards[str(ctx.author.id)].add_ship(ship)
            await ctx.channel.send("{} ship set!".format(ctx.author.mention))
        except ValueError:
            await ctx.channel.send("{} spot is occupied".format(ctx.author.mention))
        except IndexError:
            await ctx.channel.send("{} invalid spot".format(ctx.author.mention))

        if game.begin_fight():
            player_list = [await self.bot.fetch_user(int(i)) for i in game.players]
            for p in player_list:
                await p.send("Your Battleship game has begun!")

    @commands.command()
    @commands.check(is_valid_and_private)
    async def BSboard(self, ctx):
        """
        Sends the current state of your board

        Can only be sent in DMs
        """

        game = get_game(ctx.author.id)
        board_obj = game.boards[str(ctx.author.id)]
        board = board_obj.board

        gboard = "    ".join(str(i) for i in range(10)) + "\n"
        curr_s = 0
        i = 0
        for row in board:
            for s in row:
                if s[0] == None:
                    gboard += ":blue_square:"
                elif not isinstance(s[0], bool):
                    ship = board_obj.ships[s[0]]
                    gboard += ":ship:"
                elif s[0] == True:
                    gboard += ":red_circle:"
                elif s[0] == False:
                    gboard += ":white_circle:"
            gboard += f"  {i}\n"
            i += 1
            
        await ctx.channel.send(gboard)

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.id == 839539754214752287 and is_players_turn(ctx.author.id))
    async def BSfire(self, ctx, x : int, y : int):
        """
        Fires a shot at the enemy's board.

        Must happen on your turn

        Parameters:
        -----------
        x - the x position to shoot (0 - left, 9 - right)
        y - the y position to shoot (0 - up, 9 - down)
        """

        game = get_game(ctx.author.id)
        board = game.boards[[k for k in game.boards.keys() if int(k) != ctx.author.id][0]]
        
        try:
            hit, dead, ship_name = board.fire(x, y)
        except ValueError:
            await ctx.channel.send("{} - you already shot there!".format(ctx.author.mention))
            return
        
        if dead:
            await ctx.channel.send("<@!{}> :vs: <@!{}>\n**{} wins battleship!**".format(game.player_list[0], game.player_list[1], ctx.author.mention))
            game.end()
            return
        
        if hit:
            if ship_name != None:
                await ctx.channel.send("{} - you sunk your opponent's {}".format(ctx.author.mention, ship_name.capitalize()))
            else:
                await ctx.channel.send("{} - hit!".format(ctx.author.mention))
        else:            
            await ctx.channel.send("{} - miss...".format(ctx.author.mention))

        game.next_turn()

    @commands.command()
    @commands.check(lambda ctx: is_valid_player(ctx.author.id))
    async def BSturn(self, ctx):
        """
        Send whose turn it is
        """

        game = get_game(ctx.author.id)

        await ctx.channel.send("<@!{}> :vs: <@!{}>\n**It is currently <@!{}>'s turn**".format(game.player_list[0], game.player_list[1], game.player_list[game.turn]))

    @commands.command()
    @commands.check(lambda ctx: is_fighting(ctx.author.id))
    async def BSshots(self, ctx):
        """
        Send a map of the shots you've taken at your enemy
        """

        game = get_game(ctx.author.id)
        board = game.boards[[str(p) for p in game.player_list if p != ctx.author.id][0]].board

        gboard = "    ".join(str(i) for i in range(10)) + "\n"
        curr_s = 0
        i = 0
        for row in board:
            for s in row:
                if isinstance(s[0], bool):
                    if s[0] == True:
                        gboard += ":red_circle:"
                    else:
                        gboard += ":white_circle:"
                else:
                    gboard += ":blue_square:"
            gboard += f"  {i}\n"
            i += 1
        
        await ctx.channel.send("{}\n{}".format(ctx.author.mention, gboard))

    @commands.command()
    @commands.check(lambda ctx: is_valid_player(ctx.author.id))
    async def BSships(self, ctx):
        """
        Send a list of the ships you've placed and haven't placed
        """

        game = get_game(ctx.author.id)
        board = game.boards[str(ctx.author.id)]
        ships = [s.name for s in board.ships]

        string = ""
        for ship in Ship.ships.keys():
            string += f"**{ship.capitalize()}** - {Ship.ships[ship]} spots {':white_check_mark:' if ship in ships else ':negative_squared_cross_mark:'}\n"

        await ctx.channel.send("{}\n{}".format(ctx.author.mention, string))
