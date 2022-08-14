from adventure.Battle import Battle
from adventure.Scene import Scene, Option
from adventure.Player import Player
from adventure.Enemy import Slime, Goblin, SuperGoblin, DarkDragon
from comiee import fixed


class EnemyOpt(Scene):
    """选择怪物"""

    def __init__(self, session, map, player):
        super().__init__(session)
        self.options = Option()
        goto = super().goto

        for enemy in map.enemy_list:
            @self.options(enemy.name)
            @fixed(enemy)
            def _(e):
                goto(Battle, player, e())

        @self.options(0, '返回')
        def _():
            self.finish()

    async def ask(self, before='请选择怪物：', end=''):
        await super().ask(before, end)


class MapOpt(Scene):
    """选择地图"""

    def __init__(self, session):
        super().__init__(session)
        self.options = Option()
        goto = super().goto
        map_list = (NoviceVillage, EnchantedForest, ForbiddenArea)
        for map in map_list:
            @self.options(map.name)
            @fixed(map)
            def f(m):
                goto(m)

    async def ask(self, before='请选择目的地：', end=''):
        await super().ask(before, end)


class Map(Scene):
    options = Option()
    name = ''
    enemy_list = ()

    async def ask(self, before='', end=''):
        text = f'当前位置【{self.name}】，可能遭遇的怪物：\n{"、".join(i.name for i in self.enemy_list)}\n请选择：'
        return await super().ask(before or text, end)

    @options('打怪', info='（每场战斗花费10体力）')
    async def _(self):
        player = Player(self.session)
        await player.ensure_cost(10, 'stamina')
        super().goto(EnemyOpt, self, player, back=True)

    @options('移动')
    async def _(self):
        super().goto(MapOpt)

    @options(0, '退出')
    def _(self):
        self.exit()


class NoviceVillage(Map):
    name = '新手村'
    enemy_list = (Slime,)

    options = Option(Map.options)

    @options('免费治疗')
    async def _(self):
        player = Player(self.session)
        player.hp = player.max_hp
        await self.send('已恢复全部血量。')


class EnchantedForest(Map):
    name = '迷之森林'
    enemy_list = (Goblin, SuperGoblin)


class ForbiddenArea(Battle):
    name = '禁地'
    is_first_run = True

    def __init__(self, session):
        super().__init__(session, Player(session), DarkDragon())

    async def run(self):
        if self.is_first_run:
            await self.send(f'暗龙：“愚蠢的人类，胆敢打扰吾之休眠，这份罪孽，就用汝的生命偿还吧！')
            self.is_first_run = False
        await super().run()
