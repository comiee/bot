from adventure.Battle import Battle
from adventure.Scene import Scene, Option
from adventure.Player import Player
from adventure.Enemy import Slime
from adventure.EnemyGroup import Slime3
from comiee import fixed


class Opt(Scene):
    def __init__(self, session, map, player):
        super().__init__(session)
        self.options = Option()
        goto = super().goto

        for enemy in map.enemy_list:
            @self.options(enemy.name)
            @fixed(enemy)
            def _(e):
                goto(Battle, player ,e())

        @self.options(0, '返回')
        def _():
            self.finish()

    async def ask(self, before='请选择怪物：', end=''):
        await super().ask(before, end)


class Map(Scene):
    options = Option()
    name = ''
    enemy_list = ()

    async def ask(self, before='', end=''):
        return await super().ask(before or f'当前位置【{self.name}】，请选择', end)

    @options('打怪', info='（每场战斗花费10体力）')
    async def _(self):
        player = Player(self.session)
        await player.ensure_cost(10, 'stamina')
        super().goto(Opt, self, player, back=True)

    @options(0, '退出')
    def _(self):
        self.exit()


class NoviceVillage(Map):
    name = '新手村'
    enemy_list = (Slime,)# Slime3)
