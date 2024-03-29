from adventure.Enemy import Enemy
from adventure.Player import Player
from adventure.Scene import Scene, Option
from adventure.exceptions import Dead
import random


class Battle(Scene):
    """战斗"""
    options = Option()

    def __init__(self, session, player: Player, target: Enemy):
        super().__init__(session)
        self.player = player
        self.target = target

    async def run(self):
        while 1:
            try:
                await self.ask(f'''\
与{self.target}的战斗
{self.player.get_attribute()}
{self.target.get_attribute()}
请选择：''')
            except Dead as e:
                if e.entity is self.player:
                    await super().send(f'{self.player}不幸阵亡了。')
                    self.exit()
                if e.entity is self.target:
                    await super().send('战斗胜利。' + self.target.drop(self.player))
                    self.finish()

    @options('攻击')
    async def attack(self):
        result = [self.player.hurt(self.target), self.target.hurt(self.player)]
        await super().send('\n'.join(result))

    @options(0, '逃跑')
    async def _(self):
        n = random.randint(0, 10)
        self.player.cost(n)
        await super().send(f'{self.player}慌不择路地逃跑了，连钱包开了都不管了，跑出敌人的势力范围后他清点了下钱包，发现少了{n}金币')
        super().finish()
