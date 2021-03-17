from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from tools.state import in_group
from tools.sql import cur
from adventure.Player import Player
import re
import random


@on_command('打劫')
@in_group
async def _(session: CommandSession):
    match = re.search(r'\d+', session.current_arg)
    if not match:
        await session.send('你得告诉我要打劫谁啊。')
        return
    user = Player(session)
    target = Player(match.group())
    if not await target.is_group_member(session):
        await session.send('这个人并不在这个群哦。')
        return
    await user.ensure_cost(10, 'stamina')
    if cur.execute(f'select coin from info where qq={target} and coin>10;'):  # 判断目标金币是否充足
        coin = cur.fetchone()[0]
        dif = user.attack - target.defense
        if dif < 0:  # 用户攻击比目标防御低，有 1/差值 的概率失败
            if random.random() > 1 / abs(dif):  # 打劫失败，倒贴金币
                if cur.execute(f'select coin from info where qq={int(user)} and coin>0;'):
                    coin = cur.fetchone()[0]
                    result = random.randint(0, min(coin, 10))
                else:
                    result = 0
                target.gain(result)
                user.cost(result)
                await session.send(f'打劫失败，消耗10体力，损失{result}金币！')
                return
            dif = 0
        left = min(dif, coin)  # 结果的下限
        right = max(left, 10)  # 结果的上限
        result = random.randint(left, right)  # 随机结果
        user.gain(result)
        target.cost(result)
        await session.send(f'打劫成功，消耗10体力，获得{result}金币！')
    else:
        await session.send('他的金币太少了，你换个人打劫吧。')


@on_natural_language('打劫')
async def _(session: NLPSession):
    if match := re.search(r'\d+', session.msg):
        return IntentCommand(90, '打劫', current_arg=match.group())
