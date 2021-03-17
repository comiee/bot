from nonebot import CommandSession, NLPSession, IntentCommand
from tools.state import State, get_id, ModeSwitch
from tools.User import User
import re
import random
from collections import defaultdict

# 穷举无法计算的题目
bad = {(1, 1, 1, 1), (1, 1, 1, 2), (1, 1, 1, 3), (1, 1, 1, 4), (1, 1, 1, 5), (1, 1, 1, 6), (1, 1, 1, 7), (1, 1, 1, 9),
       (1, 1, 2, 2), (1, 1, 2, 3), (1, 1, 2, 4), (1, 1, 2, 5), (1, 1, 3, 3), (1, 1, 5, 9), (1, 1, 6, 7), (1, 1, 7, 7),
       (1, 1, 7, 8), (1, 1, 7, 9), (1, 1, 8, 9), (1, 1, 9, 9), (1, 2, 2, 2), (1, 2, 2, 3), (1, 2, 9, 9), (1, 3, 5, 5),
       (1, 4, 9, 9), (1, 5, 5, 7), (1, 5, 5, 8), (1, 5, 7, 7), (1, 6, 6, 7), (1, 6, 7, 7), (1, 6, 7, 8), (1, 7, 7, 7),
       (1, 7, 7, 8), (1, 8, 9, 9), (1, 9, 9, 9), (2, 2, 2, 2), (2, 2, 2, 6), (2, 2, 7, 9), (2, 2, 9, 9), (2, 3, 3, 4),
       (2, 5, 5, 5), (2, 5, 5, 6), (2, 5, 9, 9), (2, 6, 7, 7), (2, 7, 7, 7), (2, 7, 7, 9), (2, 7, 9, 9), (2, 9, 9, 9),
       (3, 3, 5, 8), (3, 4, 6, 7), (3, 4, 8, 8), (3, 5, 5, 5), (3, 5, 7, 7), (4, 4, 5, 9), (4, 4, 6, 6), (4, 4, 6, 7),
       (4, 4, 9, 9), (4, 7, 7, 9), (4, 9, 9, 9), (5, 5, 5, 7), (5, 5, 5, 8), (5, 5, 6, 9), (5, 5, 7, 9), (5, 7, 7, 7),
       (5, 7, 7, 8), (5, 7, 9, 9), (5, 8, 9, 9), (5, 9, 9, 9), (6, 6, 6, 7), (6, 6, 7, 7), (6, 6, 7, 8), (6, 6, 9, 9),
       (6, 7, 7, 7), (6, 7, 7, 8), (6, 7, 7, 9), (6, 7, 8, 8), (6, 9, 9, 9), (7, 7, 7, 7), (7, 7, 7, 8), (7, 7, 7, 9),
       (7, 7, 8, 8), (7, 7, 8, 9), (7, 7, 9, 9), (7, 8, 8, 8), (7, 8, 9, 9), (7, 9, 9, 9), (8, 8, 8, 8), (8, 8, 8, 9),
       (8, 8, 9, 9), (8, 9, 9, 9), (9, 9, 9, 9)}
question = State(None, get_id)  # 记录题目
score = State(None, get_id)  # 记录得分
count = State(lambda: 0, get_id)  # 记录答错次数


def set_question(session):
    """出题"""
    while 1:
        q = random.choices(range(1, 10), k=4)
        if tuple(sorted(q)) not in bad:
            question[session] = q
            return


@ModeSwitch('24-point', '24点')
async def p24(session: CommandSession):
    set_question(session)
    score[session] = defaultdict(lambda: 0)
    await session.send(f'''\
24点游戏开始！不玩了请说“不玩了”哦。
游戏规则：
随机抽取4个1~9的数字，请通过运算得到24（所有的数必须全部使用且只能使用一次）。
答对得5分，得分自动转为金币。
可用的运算符如下（^代表乘方）：
+ - * / ^ ( )
第一题：{question[session]}''')


@p24.end
async def _(session: CommandSession):
    text = '\n'.join(f'[CQ:at,qq={k}]\t{v}' for k, v in score[session].items())
    await session.send(f'24点游戏结束！得分情况：\n{text}\n下次想玩还可以找我哦。')
    del question[session]
    del score[session]
    del count[session]


@p24.run
async def _(session: NLPSession):
    answer = session.msg_text
    count[session] += 1
    if re.search(r'^[\d+\-*/^()（）]+$', answer):  # 判断是否是式子
        nums = [int(i) for i in re.findall(r'\d+', answer)]
        if sorted(question[session]) == sorted(nums):  # 判断使用的数
            if round(eval(answer.replace('^', '**').replace('（', '(').replace('）', ')')), 10) == 24:  # 判断式子的结果
                user = User(session)
                score[session][user] += 5
                user.gain(5)
                set_question(session)
                count[session] = 0
                await session.send(f'{user!r}答对，加五分！\n下一题：{question[session]}')
            else:
                await session.send('这个式子的结果不是24，再好好想想吧')
        else:
            await session.send('不对啦，所有的数必须全部使用且只能使用一次')
    else:
        await session.send('你在逗我吗？这压根就不是个式子')
    if count[session] >= 5:
        await session.send('答错次数过多，自动结束游戏')
        return IntentCommand(100.0, '不玩了')
