from nonebot import on_command, CommandSession
from tools.state import conversation, when
from tools.User import User
import aiohttp
import json


@on_command('色图')
@when(
    {'group_id': {694541980, 811912656, 324085758}},
    {'message_type': 'private', 'user_id': {1440667228, 2667336028}}
)
@conversation
async def _(session: CommandSession):
    user = User(session)
    yield f'{user!r}本次操作将花费30金币，是否继续？'
    await user.ask()
    if user.query() < 30:
        await session.send('余额不足！\n签到和玩游戏可以获得金币哦。')
        return
    await session.send('正在爬取，请稍候。')
    try:
        async with aiohttp.ClientSession() as clientSession:
            async with clientSession.get('https://api.lolicon.app/setu/?r18=2') as resp:
                temp = json.loads(await resp.text())
                quota = temp['quota']
                if quota:
                    url = temp['data'][0]['url']
                    result = f'{url}\n剩余额度：{quota}'
                else:
                    result = '本日调用额度已用完，请明天再来。'
    except:
        await session.send('爬取失败，金币已返还。')
    else:
        assert user.cost(30)  # 爬取成功才扣钱
        await session.send(result)
