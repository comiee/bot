from nonebot import on_command, CommandSession
from tools.sql import is_ban
import json


@on_command('洗脑')
async def _(session: CommandSession):
    if is_ban(session):
        await session.send('你已被列入黑名单，无法使用此命令')
        return
    if session.ctx['raw_message'][:3] != '洗脑 ':
        return
    q, a, *_ = *session.ctx['raw_message'][3:].split('#', 1), ''

    file = 'data/teach.json'
    with open(file, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
        if q not in data:
            await session.send(f'小魅的大脑中并没有关于“{q}”的记忆哦。')
            return
        if not a:
            if session.ctx['user_id'] == 1440667228:
                del data[q]
            else:
                await session.send('只有小魅的主人能使用批量洗脑功能哦。')
                return
        else:
            if a not in data[q]:
                await session.send('小魅并不记得这个回答哦。')
                return
            data[q].remove(a)
            if not data[q]:
                del data[q]
        with open(file, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, ensure_ascii=False)
        await session.send('唉？这个回答是不对的吗？好吧，小魅不会这么说了。')


@on_command('显示')
async def _(session: CommandSession):
    if session.ctx['raw_message'][:3] != '显示 ':
        return
    q = session.ctx['raw_message'][3:]
    with open('data/teach.json', encoding='utf-8') as f:
        data = json.load(f)
        if q in data:
            await session.send(repr(data[q]))
        else:
            await session.send(f'小魅的大脑中并没有关于“{q}”的记忆哦。')
