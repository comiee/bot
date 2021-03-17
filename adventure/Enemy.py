from adventure.Entity import Entity


class Enemy(Entity):
    def __init__(self):
        self.hp = self.max_hp
        self.live = True

    def __str__(self):
        return self.name

    def drop(self, player):
        return ''


class Slime(Enemy):
    name = '史莱姆'
    max_hp = 1
    attack = 1
    defense = 1

    def drop(self, player):
        player.gain(1)
        return f'{player}获得了1金币'
