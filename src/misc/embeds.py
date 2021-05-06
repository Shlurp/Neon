import discord
from discord.ext import commands

def get_embed(path : str, ctx : commands.Context) -> discord.Embed:
    with open(path, "r") as f:
        curr = None
        header = {"title" : "\u200b", "description" : None, "color" : 0}
        field = {}
        embed = None
        des = False

        while True:

            curr = f.readline()
            if curr == "":
                break
            curr = curr.strip()
            if curr == "":
                continue
            
            if embed == None:
                if curr.startswith("TITLE"):
                    des = False
                    header["title"] = curr[curr.index(':')+1:].strip()

                elif curr.startswith("COLOR"):
                    des = False
                    header["color"] = int(curr[curr.index(':')+1:].strip().replace('#', '0x'), 0)

                elif curr.startswith("DESCRIPTION"):                    
                    header["description"] = curr[curr.index(':')+1:].strip()
                    des = True

                elif curr.startswith("FOOTER"):
                    des = False
                    header["footer"] = curr[curr.index(':')+1:].strip()

                elif curr.startswith("THUMBNAIL"):
                    des = False
                    s = curr[curr.index(':')+1:]
                    if '{' in s and '}' in s:
                        d = s[s.index('{')+1:s.index('}')]
                        if d == "icon":
                            header["thumbnail"] = ctx.guild.icon_url
                    else:
                        header["thumbnail"] = s
                elif curr.startswith("#create"):
                    des = False
                    embed = discord.Embed(title=header["title"], description=header["description"], color=header["color"])
                    if "thumbnail" in header:
                        embed.set_thumbnail(url=header["thumbnail"])
                    if "footer" in header:
                        embed.set_footer(text=header["footer"])
                elif des:
                    header["description"] += curr
                else:
                    raise SyntaxError("Invalid line: {}".format(curr))
            
            elif curr.startswith("#field"):
                try:
                    field_name = curr[curr.index('{')+1:curr.index('}')]
                except ValueError:
                    field_name = "\u200b"
                try:
                    metadata = [i.strip() for i in curr[curr.index('[')+1:curr.index(']')].split(',')]
                except ValueError:
                    metadata = []
                
                field_data = ""
                while not curr.startswith("#createfield"):
                    curr = f.readline()
                    if curr.startswith("#createfield"):
                        break
                    if curr == "":
                        break
                    curr.replace('\n', '')
                    if curr == "":
                        curr = "\u200b"
                        continue
                    
                    i = 0
                    while i < len(curr):
                        c = curr[i]

                        if c == '{':
                            i += 1
                            o = curr[i]
                            data = ""
                            while c != '}':
                                i += 1
                                c = curr[i]
                                if c != '}':
                                    data += c
                            
                            if o == '#':
                                d = discord.utils.get(ctx.guild.channels, name=data)
                                if d == None:
                                    d = discord.utils.get(ctx.guild.channels, id=int(data))
                                field_data += str(d)
                            elif o == '@':
                                d = discord.utils.get(ctx.guild.members, name=data)
                                if d == None:
                                    d = discord.utils.get(ctx.guild.members, id=int(data))
                                field_data += str(d.mention)
                            elif o == ':':
                                field_data += str(discord.utils.get(ctx.guild.emojis, name=data))
                        else:
                            field_data += c
                        
                        i += 1
                embed.add_field(name=field_name, value=field_data, inline="inline" in metadata)

    return embed
