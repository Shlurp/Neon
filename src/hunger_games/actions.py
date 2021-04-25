from hunger_games.hgames_objs import *
import random

def attack(offending : Tribute):
    opponents = [i for i in HGgame.tribute_map[offending.y][offending.x].tributes if i != offending.id]
    if len(opponents) < 1:
        return (None, None, None, None)

    defending = random.choice(opponents)
    attacker_i = random.randint(0, 2) % 2
    attacker = [offending.id, defending][attacker_i]
    victim = [offending.id, defending][1 - attacker_i]

    attacker = HGgame.tributes[str(attacker)]
    victim = HGgame.tributes[str(victim)]

    weapon = random.choice(list(attacker.weapons))

    if attacker.reduce_stamina(weapon.exertion) == -1:
        return (0, attacker, victim, weapon)        # Return list of data. First value represents the state of the action
                                                    # 0 means failure
                                                    # 1 means success
                                                    # -1 means death
    
    if victim.take_damage(weapon.damage) == -1:
        return (-1, attacker, victim, weapon)

    return (1, attacker, victim, weapon)

def search(tribute : Tribute):
    found = random.randint(0, 2)

    if found != 0:
        return None
    
    weapon = Weapons_Cache.get_random_weapon(HGgame.tribute_map[tribute.y][tribute.x].rarity)
    if weapon != None:
        tribute.add_weapon(weapon)
    return weapon

def remove_weapon(tribute : Tribute, weapon_name):
    return tribute.remove_weapon(weapon_name)

def get_danger_map(tx, ty):
    num_t = len(HGgame.tributes)
    green = lambda x,y: len(HGgame.tribute_map[y][x].tributes) <= 0
    yellow = lambda x,y: len(HGgame.tribute_map[y][x].tributes) <= num_t // 3
    orange = lambda x,y: len(HGgame.tribute_map[y][x].tributes) <= num_t // 2
    red = lambda x,y: len(HGgame.tribute_map[y][x].tributes) <= num_t
    
    dmap = []
    i = 0
    for y in range(len(HGgame.tribute_map)):
        dmap.append(list())
        for x in range(len(HGgame.tribute_map[y])):
            if green(x, y):
                dmap[i].append(":green_square:" if x != tx or y != ty else ":green_circle:")
            elif yellow(x, y):
                dmap[i].append(":yellow_square:" if x != tx or y != ty else ":yellow_circle:")
            elif orange(x, y):
                dmap[i].append(":orange_square:" if x != tx or y != ty else ":orange_circle:")
            elif red(x, y):
                dmap[i].append(":red_square:" if x != tx or y != ty else ":red_circle:")
        i += 1

    return dmap

    