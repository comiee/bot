from adventure.Enemy import Enemy, Slime
from adventure.exceptions import Dead


class EnemyGroup(Enemy):
    enemy_list = []
    selected = None

    def select(self, n):
        if n is None:
            self.selected = None
            self.name = type(self).name
        else:
            self.selected = self.enemy_list[n]
            self.name = self.selected.name

    def get_attribute(self):
        return '\n'.join(e.get_attribute() for e in self.enemy_list)

    def injured(self, n):
        try:
            self.selected.injured(n)
        except Dead as d:
            self.enemy_list.remove(d.entity)
            if not self.enemy_list:
                self.dead()
        self.select(None)

    def treat(self, n):
        self.selected.treat(n)
        self.select(None)

    def hurt(self, target):
        return '\n'.join(e.hurt(target) for e in self.enemy_list)


class Slime3(EnemyGroup):
    name = '史莱姆三人众'

    def __init__(self):
        super().__init__()
        self.enemy_list = [Slime().set_name('史莱姆大哥'), Slime().set_name('史莱姆二哥'), Slime().set_name('史莱姆小弟')]
