from random import *
import math
from global_objs import *

class Tribute:
    def __init__(self, discord_id, x=3, y=3):
        self.id = discord_id
        self.inventory = []
        self.weapons = set([Weapons_Cache.fist])
        self.health = 10
        self.stamina = 100
        self.x = x
        self.y = y

    def __str__ (self):
        return "<@!{}>".format(self.id)

    def take_damage(self, damage):
        self.health -= damage

        if(self.health <= 0):
            return -1
        return 0

    def reduce_stamina(self, stamina):
        if(self.stamina <= stamina):
            return -1

        self.stamina -= stamina
        return 0

    def remove_weapon(self, weapon_name):
        found = False
        weapon_name = weapon_name.lower()

        if len(self.weapons) <= 1:
            raise IndexError
        if weapon_name == "fist":
            raise ValueError

        for weapon in self.weapons:
            if weapon.name == weapon_name:
                found = True
                self.weapons.remove(weapon)
                break

        return found


    add_weapon = lambda self, weapon : self.weapons.add(weapon)

class Weapon:
    def __init__(self, name, damage, exertion, rarity=0):
        self.name = name
        self.damage = damage
        self.exertion = exertion
        self.rarity = rarity
        
    def __str__ (self):
        return self.name

class Weapons_Cache:
    fist = Weapon("fist", 1, 0)
    weapons = (
        Weapon("sword", 3, 2, 5),
        Weapon("rock", 2, 3, 0),
        Weapon("knife", 2, 1, 3),
        Weapon("gun", 6, 1, 10),
        )
    
    @staticmethod
    def get_random_weapon(rarity):
        return choice([weapon for weapon in Weapons_Cache.weapons if weapon.rarity <= rarity])

class Map_Square():
    def __init__(self, rarity):
        self.rarity = rarity
        self.tributes = []

class HungerGames_game (Game):
    def __init__(self):
        super().__init__("hunger games")

    def begin (self):
        if len(self.player_list) < self.min_players:
            raise ValueError

        self.tributes = {}
        self.tribute_map = [[Map_Square(math.ceil(10 - 10 / (3 * math.sqrt(2)) * math.sqrt((i - 3) ** 2 + (j - 3) ** 2))) for j in range(7)] for i in range(7)]
        for player_id in self.player_list:
            t = Tribute(player_id)
            self.tributes[str(player_id)] = t
            self.tribute_map[t.y][t.x].tributes.append(t.id)

        self.begun = True

    def remove_player_from_map(self, tribute_id):
        t = self.tributes[str(tribute_id)]
        self.tribute_map[t.y][t.x].tributes.remove(t.id)
    
    def move_player(self, tribute_id, dx : int, dy : int):
        t = self.tributes[str(tribute_id)]
        if t.x + dx < 0 or t.x + dx >= len(self.tribute_map[0]) or t.y + dy < 0 or t.y + dy >= len(self.tribute_map):
            raise IndexError
            
        self.tribute_map[t.y][t.x].tributes.remove(t.id)
        t.x += dx
        t.y += dy
        self.tribute_map[t.y][t.x].tributes.append(t.id)


HGgame = HungerGames_game()