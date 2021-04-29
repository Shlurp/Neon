from battleship.battleship_objs import *
import discord
from discord.ext import commands

def get_game(p_id) -> BattleshipGame:
    battleships = Game.games["battleship"]

    for b in battleships:
        if int(p_id) in b.player_list:
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
            return b.players[b.turn] == int(p_id) and b.fighting
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

class Battleship_Cog (commands.Cog, name="Battleship Commands"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.type != discord.ChannelType.private and not is_valid_player(ctx.author.id))
    async def BSjoin(self, ctx):
        try:
            last_game = Game.games["battleship"][-1]
        except KeyError:
            last_game = None

        if last_game == None or len(last_game.player_list) >= last_game.max_players:
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
    @commands.check(lambda ctx: ctx.channel.type == discord.ChannelType.private and not is_fighting(ctx.author.id))
    async def BSset(self, ctx, shipname : str, direction : str, x0 : int, y0 : int):
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
            players = [await self.bot.fetch_user(int(i)) for i in game.player_list]
            for p in players:
                await p.send("Your Battleship game has begun!")

    @commands.command()
    @commands.check(is_valid_and_private)
    async def BSboard(self, ctx):
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
                    ship = board_obj.boats[s[0]]
                    gboard += ":ship:"
                elif s[0] == True:
                    gboard += ":red_circle:"
                elif s[0] == False:
                    gboard += ":white_circle:"
            gboard += f"  {i}\n"
            i += 1
            
        await ctx.channel.send(gboard)

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.type != discord.ChannelType.private and is_players_turn(ctx.author.id))
    async def BSfire(self, ctx, x : int, y : int):
        game = get_game(ctx.author.id)
        board = game.boards[[k for k in game.boards.keys() if int(k) != ctx.author.id][0]]
        
        try:
            hit, dead, boat_name = board.fire(x, y)
        except ValueError:
            await ctx.channel.send("{} - you already shot there!".format(ctx.author.mention))
            return
        
        if dead:
            await ctx.channel.send("<@!{}> :vs: <@!{}>\n**{} wins battleship!**".format(game.players[0], game.players[1], ctx.author.mention))
            game.end()
            return
        
        if hit:
            if boat_name != None:
                await ctx.channel.send("{} - you sunk your opponent's {}".format(ctx.author.mention, boat_name.capitalize()))
            else:
                await ctx.channel.send("{} - hit!".format(ctx.author.mention))
        else:            
            await ctx.channel.send("{} - miss...".format(ctx.author.mention))

        game.next_turn()

    @commands.command()
    @commands.check(lambda ctx: is_valid_player(ctx.author.id))
    async def BSturn(self, ctx):
        game = get_game(ctx.author.id)

        await ctx.channel.send("<@!{}> :vs: <@!{}>\n**It is currently <@!{}>'s turn**".format(game.players[0], game.players[1], game.players[game.turn]))

    @commands.command()
    @commands.check(lambda ctx: is_fighting(ctx.author.id))
    async def BSshots(self, ctx):
        game = get_game(ctx.author.id)
        board = board_obj = game.boards[[str(p) for p in game.players if p != ctx.author.id][0]].board

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
