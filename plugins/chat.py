from nonebot import on_command, CommandSession
from nonebot.log import logger
from tools.state import State, get_id, mode, on_message, on_mode, when
from tools.User import User
from tools.sql import cur, is_ban
import re
import random
import json

exec('from datetime import datetime;'
     'from tools.functions import to_int;')

last = State(lambda: ['', 0], get_id)


@on_command('开', aliases=('开启', '聊天'))
async def _(session: CommandSession):
    if mode[session] == 'chat':
        await session.send('聊天功能已经是开启状态了哦。')
    else:
        user = User(session)
        await user.ask('是否确认花10金币开启聊天功能？（下次小魅的主人重启小魅时聊天功能将恢复为开启状态）')
        await user.ensure_cost(10)
        await session.send('聊天功能已开启，快来和我聊天吧！')
        mode[session] = 'chat'


@on_command('关', aliases=('关闭', '闭嘴'))
async def _(session: CommandSession):
    if mode[session] == 'chat':
        user = User(session)
        await user.ask('是否确认花10金币关闭聊天功能？（下次小魅的主人重启小魅时聊天功能将恢复为开启状态）')
        await user.ensure_cost(10)
        await session.send('聊天功能已关闭。')
        mode[session] = ''
    else:
        await session.send('我已经闭嘴了，你还要我怎样？')


@on_message
@on_mode('chat')
@when({'user_id': {3031315187, 1790218632, 1845455477, 2854196306, 1793979796, 2150533306}}, black_list=True)
async def _(session):
    """处理聊天"""
    text = session.ctx['raw_message']
    user = User(session)

    async def send(s):
        # 处理黑名单
        if is_ban(session):
            if cur.execute(f'select * from ban where qq={user} and date!=curdate();'):
                cur.execute(f'update ban set count=10,date=curdate() where qq={user};')
            if cur.execute(f'select * from ban where qq={user} and count>=0'):
                cur.execute(f'update ban set count=count-1 where qq={user};')
            if cur.execute(f'select count from ban where qq={user} and count<=0;'):
                if cur.fetchone()[0] == 0:
                    await session.send('你在黑名单里，主人不让我和你多说话。')
                return
        await session.send(s)
        logger.info('信息为：' + text)
        logger.info('已发送：' + s)

    # 处理复读
    global last
    last_text, last_num = last[session]
    if last_text == text:
        last[session][1] += 1
        if 3 <= last_num <= 5:
            await send(['复读机？', '一直重复一句话有意思吗？', '再这样我就不理你了！'][last_num - 3])
        if 3 <= last_num:
            return
    else:
        last[session] = [text, 1]

    # 处理艾特自己
    if f'[CQ:at,qq={session.self_id}]' in text:
        text = re.sub(fr'\[CQ:at,qq={session.self_id}\] ?', '', text)
        if not text:
            await send('有什么事你倒是说啊')
            return

    # 读文件发送对应回复
    with open('data/chat.txt', encoding='utf-8') as f:
        for line in f.readlines():
            data = line.strip().split('\t')
            pattern, probability, *_ = *data.pop(0).split('%%'), ''
            if not probability or random.random() < eval(probability):
                if match := re.search(pattern, text, re.S):
                    logger.debug('匹配到：' + match.group())
                    await send(eval(f"""f'''{random.choice(data)}'''"""))
                    return
    with open('data/teach.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if text in data:
            await send(random.choice(data[text]))
