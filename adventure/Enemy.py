from adventure.Entity import Entity
import random


class Enemy(Entity):
    """怪物"""

    def __init__(self):
        self.hp = self.max_hp
        self.live = True

    def __str__(self):
        return self.name

    def drop(self, player):
        """执行掉落代码，返回结果字符串"""
        return ''


# 下面是具体的怪物


class Slime(Enemy):
    name = '史莱姆'
    max_hp = 1
    attack = 1
    defense = 0

    def drop(self, player):
        player.gain(1)
        return f'{player}获得了1金币'


class Goblin(Enemy):
    name = '哥布林'
    max_hp = 10
    attack = 2
    defense = 2

    def drop(self, player):
        coin = random.randint(1, 3)
        player.gain(coin)
        return f'{player}获得了{coin}金币'


class SuperGoblin(Goblin):
    name = '精英哥布林'
    max_hp = 20
    attack = 5

    def drop(self, player):
        player.gain(5)
        return f'{player}获得了5金币'


class DarkDragon(Enemy):
    name = '暗龙'
    max_hp = 1000
    attack = 100
    defense = 100

    def drop(self, player):
        player.gain(10000)
        player.hp = player.max_hp
        player.gain(200, 'stamina')
        player.add_buff(9, 60 * 60)
        return f'''
恭喜{player}击杀了暗龙，获得了10000金币；
暗龙蕴含着强大的力量的血溅到了{player}身上，生命回满，体力+200；
获得1小时的【暗龙诅咒】效果，攻击+100，防御-100。'''
