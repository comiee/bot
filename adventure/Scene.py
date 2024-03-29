from nonebot import CommandSession
from adventure.Option import Option
from adventure.exceptions import Finish, Exit
from asyncio import iscoroutinefunction


class Scene:
    """场景"""

    options = Option()

    def __init__(self, session: CommandSession):
        self.session = session

    @property
    def stack(self):
        return self.session.state['stack']

    async def send(self, *args, **kwargs):
        return await self.session.send(*args, **kwargs)

    async def ask(self, before='请选择：', end=''):
        """询问玩家的选择，选项由options确定"""
        text = '\n'.join(filter(bool, [before, str(self.options), end]))
        while 1:
            answer = self.session.get('answer', prompt=text)
            del self.session.state['answer']
            if answer in self.options:
                return await self.select(answer)
            text = '选项错误，请重新选择：'

    async def select(self, key):
        """执行选项"""
        fun = self.options[key]
        if iscoroutinefunction(fun):
            return await fun()
        else:
            return fun()

    def finish(self):
        """场景完成，返回上一场景"""
        raise Finish()

    def exit(self):
        """游戏结束，退出"""
        raise Exit()

    def goto(self, scene, *args, back=False, **kwargs):
        """移动到另一场景

        :param scene: 下一个场景，如果是类而非实例，则会根据args和kwargs生成实例
        :param back: 当下一场景完成时，是否会返回此场景
        """
        if isinstance(scene, type):
            scene = scene(self.session, *args, **kwargs)
        if not back:
            self.stack.pop()
        self.stack.append(scene)

    async def run(self):
        await self.ask()
