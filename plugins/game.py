from nonebot import on_command, CommandSession, permission
from adventure.exceptions import Finish, Exit
from adventure.Player import Player
from adventure.Map import NoviceVillage
from tools.state import over_mode, conversation
from functools import partial


@on_command('冒险')
@over_mode
async def _(session: CommandSession):
    if not Player(session).live:
        await session.send('你已经死亡，请复活后再试。', at_sender=True)
    else:
        while 1:
            try:
                await session.state.setdefault('stack', [NoviceVillage(session)])[-1].run()
            except Finish:
                session.state['stack'].pop()
            except Exit:
                break

        await session.send('游戏结束。')


@on_command('复活')
@conversation
async def _(session: CommandSession):
    player = Player(session)
    send = partial(session.send, at_sender=True)
    if player.live:
        await send('你并没有死亡，不需要复活。')
    else:
        yield f'{player!r}确认花费100金币复活？'
        await player.ask()
        await player.ensure_cost(100)
        player.revive()
        await send('你已复活！')
