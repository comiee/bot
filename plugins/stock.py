from nonebot import on_command, CommandSession, scheduler
from nonebot.log import logger
from tools.User import User
from tools.state import conversation
from datetime import datetime, timedelta
import math
import random

hour = datetime.strptime(datetime.now().strftime('%Y %m %d %H'), '%Y %m %d %H') + timedelta(hours=1)


@scheduler.scheduled_job('interval', hours=1, start_date=hour)
async def _():
    while dif := int(random.normalvariate(0, 1) * 10000):
        if 1000 < User(0).query('stock') + dif < 300000:  # 0.1~30
            break
    logger.info(f'股价已变动，增量为{dif / 10000}')
    User(0).gain(dif, 'stock')


@on_command('股市', aliases=('股票',))
@conversation
async def _(session: CommandSession):
    user = User(session)
    price = User(0).query('stock') / 10000
    quantity = user.query('stock')
    money = user.query('coin')
    count = yield f'''\
当前股价为{price}，你持有的股份为{quantity}，你拥有的金币为{money}。
小魅开机的时候每到整点会随机更新股价。
买入花费的金币自动向上取整，卖出花费的金币自动向下取整。
请输入操作的股份数量（正数为买入，负数为卖出）：'''
    if price != User(0).query('stock') / 10000:
        await session.send('股价已变动，请重新操作。')
        return
    count = count.replace(' ', '').replace('买入', '').replace('卖出', '-')
    try:
        count = int(count)
    except:
        await session.send('错误的输入，命令已取消。')
    else:
        coin = math.ceil(price * count)
        await user.ensure_cost(coin)
        if user.cost(-count, 'stock'):
            if coin >= 0:
                await session.send(f'购买成功，花费{coin}金币')
            else:
                await session.send(f'出售成功，获得{-coin}金币')
        else:
            user.gain(coin)
            await session.send('持有的股份不足。')


@on_command('股价', aliases=('股份',))
async def _(session: CommandSession):
    user = User(session)
    price = User(0).query('stock') / 10000
    quantity = user.query('stock')
    await session.send(f'当前股价为{price}，你持有的股份为{quantity}')
