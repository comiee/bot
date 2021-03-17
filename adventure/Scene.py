from nonebot import CommandSession
from tools.state import InSession
from adventure.Option import Option
from adventure.exceptions import Finish, Exit
from asyncio import iscoroutinefunction


class Scene(InSession):
    options = Option()

    def __init__(self, session: CommandSession):
        super().__init__(session)

    @property
    def stack(self):
        return self.session.state['stack']

    async def send(self, *args, **kwargs):
        return await self.session.send(*args, **kwargs)

    async def ask(self, before='请选择：', end=''):
        text = '\n'.join(filter(bool, [before, str(self.options), end]))
        while 1:
            answer = self.session.get('answer', prompt=text)
            del self.session.state['answer']
            if answer in self.options:
                return await self.select(answer)
            text = '选项错误，请重新选择：'

    async def select(self, key):
        fun = self.options[key]
        if iscoroutinefunction(fun):
            return await fun()
        else:
            return fun()

    def finish(self):
        raise Finish()

    def exit(self):
        raise Exit()

    def goto(self, scene, *args, back=False, **kwargs):
        if isinstance(scene, type):
            scene = scene(self.session, *args, **kwargs)
        if not back:
            self.stack.pop()
        self.stack.append(scene)

    async def run(self):
        await self.ask()
