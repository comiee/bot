from nonebot import on_command, CommandSession
from tools.state import in_group
from tools.sql import cur
from tools.User import User


@on_command('奖池')
async def _(session: CommandSession):
    jackpots = {0: '老虎机'}
    await session.send('目前奖池余额如下：\n' + '\n'.join(f'{v}：{User(k).query()}金币' for k, v in jackpots.items()))


@on_command('金币排行', aliases=('排行', '排行榜'))
@in_group
async def _(session: CommandSession):
    member_list = await session.bot.get_group_member_list(**session.ctx)
    user_list = {str(i['user_id']): i['card'] or i['nickname'] for i in member_list}
    cur.execute('select qq,coin from info order by -coin;')
    coin_list = '\n'.join(f'{coin:5d}\t{user_list[qq]}' for qq, coin in cur.fetchall() if qq in user_list)
    await session.send('本群金币排行榜\n金币\t用户\n' + coin_list)
