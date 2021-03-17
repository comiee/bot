from nonebot import on_command, CommandSession, NLPSession, IntentCommand, permission
from tools.state import State, get_id, on_message, on_mode, ModeSwitch
from tools.User import User
import json
from collections import defaultdict
import random
import re

with open('data/idioms.json', encoding='utf-8') as f:
    data = json.load(f)  # 原始数据，首字可能和键不一样，用于和小冰对接
    data_true = {}  # 处理后的数据，首字和键一样，用于成语接龙游戏
    for i in data.values():
        for j in i:
            data_true.setdefault(j[0], []).append(j)

state = State(None, get_id)  # 记录得分
target = State(None, get_id)  # 记录题目
count = State(lambda: 0, get_id)  # 记录答错次数


def get_next(session):
    if temp := [v for v in data_true.get(target[session], []) if v[-1] in data_true]:  # 排除掉无法再接的难题
        text = random.choice(temp)
        target[session] = text[-1]
        return text


@ModeSwitch('idioms', '成语接龙')
async def idioms(session: CommandSession):
    state[session] = defaultdict(lambda: 0)
    while 1:
        target[session] = random.choice(list(data_true))
        if text := get_next(session):
            await session.send(f'''\
成语接龙开始！
每接对一词得1分，打败小魅得5分，得分自动转为金币。
不玩了请说“不玩了”哦。
我先来，【{text}】''')
            break


@idioms.end
async def _(session: CommandSession):
    score = '\n'.join(f'[CQ:at,qq={k}]\t{v}' for k, v in state[session].items())
    await session.send(f"成语接龙结束！得分情况：\n{score}\n以上得分已自动转为金币，下次想玩还可以找我哦。")
    del state[session]
    del target[session]
    del count[session]


@idioms.run
async def _(session: NLPSession):
    """用于接龙游戏"""
    text = session.msg
    count[session] += 1

    if text and text[0] == target[session]:  # 判断首字是否正确
        if text in data_true[target[session]]:  # 判断答案是否在库中
            user = User(session)
            target[session] = text[-1]
            count[session] = 0
            if text := get_next(session):
                state[session][user] += 1
                user.gain(1)
                await session.send(f'{user!r}答对，加一分！\n我接【{text}】\n下面请从“{target[session]}”开始接龙！')
            else:
                state[session][user] += 5
                user.gain(5)
                await session.send(f'好吧，我接不上来了，是我输了。\n{user!r}加五分！')
                return IntentCommand(100.0, '不玩了')
        else:
            await session.send('小魅的成语库里面并没有这个成语哦。')
    else:
        await session.send(f'不对不对，要从“{target[session]}”开始接啦！')
    if count[session] >= 10:
        count[session] = 0
        text = get_next(session)
        await session.send(f'算了算了，还是我自己接吧，【{text}】，下面请从“{target[session]}”开始接龙。')


@on_message
@on_mode('chat')
async def _(session):
    """用于和小冰对接"""
    text = session.ctx['raw_message']

    if session.ctx['user_id'] != 2854196306:
        return

    if match := re.search(r'【(.*)】', text, re.S):
        if match.group(1) in {'猜歌名'}:
            return
        if (key := match.group(1)[-1]) in data:
            await session.send('[CQ:at,qq=2854196306]' + random.choice(data[key]))
        else:
            await session.send('主人快来帮我，我接不上了！')


@on_command('add', permission=permission.SUPERUSER)
async def _(session: CommandSession):
    k, v = session.current_arg.strip().split()
    data.setdefault(k, []).append(v)
    with open('data/idioms.json', 'w', encoding='utf-8') as fout:
        json.dump(data, fout, ensure_ascii=False)
    await session.send('[CQ:at,qq=2854196306]' + v)


@on_command('del', permission=permission.SUPERUSER)
async def _(session: CommandSession):
    text = session.current_arg.strip()
    data[text[0]].remove(text)
    if not data[text[0]]:
        del data[text[0]]
    with open('data/idioms.json', 'w', encoding='utf-8') as fout:
        json.dump(data, fout, ensure_ascii=False)
    await session.send('[CQ:at,qq=2854196306]' + random.choice(data[text[0]]))
