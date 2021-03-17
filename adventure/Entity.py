from adventure.exceptions import Dead


class Entity:
    name = ''  # 名字
    live = True  # 是否存活
    max_hp = 0  # 最大血量
    hp = 0  # 血量
    attack = 0  # 攻击
    defense = 0  # 防御

    def __bool__(self):
        return self.live

    def set_name(self, name):
        self.name = name
        return self

    def get_attribute(self):
        return f'{self}：血量{int(self.hp)}/{int(self.max_hp)} 攻击{int(self.attack)} 防御{int(self.defense)}'

    def injured(self, n):
        """受伤"""
        hp = self.hp - n
        if hp <= 0:
            self.dead()
        else:
            self.hp = hp

    def treat(self, n):
        """治疗"""
        self.hp = max(self.max_hp, self.hp + n)

    def dead(self):
        """死亡"""
        self.hp = 0
        self.live = False
        raise Dead(self)

    def hurt(self, target):
        """攻击目标"""
        n = max(0, self.attack - target.defense)
        target.injured(n)
        return f'{self}对{target}发起了攻击，造成了{n}点伤害'
