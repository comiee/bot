from tools.sql import cur, is_columns
from tools.User import User
from adventure.Entity import Entity


class Attr(int):
    """属性值，除了显示的时候使用s外，其他均和int一致"""

    def __new__(cls, n, s):
        obj = super().__new__(cls, n)
        obj.s = s
        return obj

    def __str__(self):
        return self.s


class Attribute:
    """属性"""

    def __init__(self, name):
        self.name = name

    def __get__(self, player, _):
        user = int(player)
        data = []  # 存储结果
        # 基础属性，如果不存在则添加
        if not cur.execute(f'select {self.name} from attribute where qq={user};'):
            cur.execute(f'insert into attribute(qq) values({user});')
            cur.execute(f'select {self.name} from attribute where qq={user};')
        data.append(cur.fetchone()[0])
        # 装备加成
        if is_columns('armor_id', self.name) and cur.execute(f'''
            select {self.name} from equipment inner join armor_id on equipment.id=armor_id.id 
            where qq={user} and {self.name}>0;
        '''):
            data.extend(Attr(i[0], '%+d' % i) for i in cur.fetchall())
        # buff加成
        if is_columns('buff_id', self.name) and cur.execute(f'''
            select {self.name},timestampdiff(second,now(),time) from effect inner join buff_id 
            on effect.buff=buff_id.buff where qq={user} and time>=now();
        '''):
            data.extend(Attr(i[0], '%+d[剩%d秒]' % i) for i in cur.fetchall())

        return Attr(sum(data), f'{sum(data)}（{"".join(map(str, data))}）')

    def __set__(self, player, value):
        user = int(player)
        value = int(value)
        cur.execute(f'''
            insert into attribute(qq,{self.name}) values({user},{value}) 
            on duplicate key update {self.name}={value};
        ''')


class Player(User, Entity):
    """玩家"""
    max_hp = Attribute('max_hp')
    hp = Attribute('hp')
    attack = Attribute('attack')
    defense = Attribute('defense')

    def __str__(self):
        return self.name

    def __repr__(self):
        return super().__repr__()

    @property
    def live(self):
        return self.hp > 0

    @live.setter
    def live(self, value):
        if value is False:
            self.hp = 0

    def revive(self):
        """复活"""
        self.hp = self.max_hp
