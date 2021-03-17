from nonebot import on_command, CommandSession
from tools.state import conversation
from tools.User import User
import numpy as np
import random
from functools import partial


class Victor(Exception):
    """胜利者"""

    def __init__(self, v):
        self.value = v


class Board:
    """棋盘"""

    def __init__(self):
        self.data = np.zeros((3, 3), dtype=int)

    def __iter__(self):
        return iter(self.data)

    def __str__(self):
        return '\n'.join(' '.join('□○×'[j] for j in i) for i in self.data)

    def judge(self, n, player):
        """落子并判断胜负
        n：落子编号
        player：落子玩家（1：用户，2：AI）
        结果：是否成功落子，如果胜负已分则抛出Victor异常
        """
        n = int(n)
        pos = divmod(n - 1, 3)
        if self.data[pos] != 0:  # 落子位置不为空，落子失败
            return False
        self.data[pos] = player

        # 判断胜负
        a = np.eye(3, dtype=bool)
        b = a[::-1]
        if any(np.all(self.data[i] == player) for i in [(pos[0], ...), (..., pos[1]), a, b]):
            raise Victor(player)
        if 0 not in self.data:
            raise Victor(0)
        return True


def ai(board):
    lines = (
        (0, ...), (1, ...), (2, ...),
        (..., 0), (..., 1), (..., 2),
        np.eye(3, dtype=bool), np.eye(3, dtype=bool)[::-1],
    )
    # 判断是否有快要成的棋，如果是自己就成，如果是敌人就堵
    for p in 2, 1:
        for i in lines:
            if sorted(board[i]) == [0, p, p]:
                board[i] = np.where(board[i] == 0, -1, p)
                x, y = np.argwhere(board == -1)[0]
                board[x, y] = 0
                return x * 3 + y + 1
    # 中间为空则落子中间
    if board[1, 1] == 0:
        return 5
    # 针对19套路，随机占边
    temp = np.array([[1, 0, 0], [0, 2, 0], [0, 0, 1]])
    if np.all(board == temp) or np.all(board == temp[::-1]):
        return random.choice([2, 4, 6, 8])
    # 针对24套路，堵两路的交点
    if len(board != 0) == 3:
        for i in 1, 3, 7, 9:
            x, y = divmod(i - 1, 3)
            if board[x, y] == 0 and np.any(board[x, :]) and np.any(board[:, y]):
                return i
    # 有角则占角
    if 0 in board[::2, ::2]:
        x, y = random.choice(np.argwhere(board[::2, ::2] == 0))
        return x * 2 * 3 + y * 2 + 1
    # 全部不满足就在空位置随机抽一个
    x, y = random.choice(np.argwhere(board == 0))
    return x * 3 + y + 1


@on_command('井字棋')
@conversation
async def _(session: CommandSession):
    board = Board()
    send = partial(session.send, at_sender=True)
    await send('''\
井字棋游戏开始！
你执○先手，小魅执×后手。
获胜得10000金币，平局得5金币，失败无收益。
回复“不玩了”退出，回复1~9在棋盘对应位置落子：''')
    try:
        while (text := (yield)) != '不玩了':
            if len(text) == 1 and '1' <= text <= '9':  # 判断玩家输入是否合法
                p = int(text)
                if board.judge(p, 1):  # 玩家落子
                    e = ai(board.data)  # AI计算
                    assert board.judge(e, 2)  # AI落子
                    await send(f'你落子{p}号位置，小魅落子{e}号位置。现在棋盘：\n{board}\n请继续落子：')
                else:
                    await send('这个位置已经有子了，好好看清楚呀！')
            else:
                await send('请输入正确序号')
        else:
            await send('好吧，欢迎再玩哦。')
    except Victor as v:
        mes = [
            '看来势均力敌呢，恭喜获得5金币。欢迎再战哦。',
            '恭喜你赢了！获得10000金币，想要再玩还可以找我哦。',
            '哼哼哼，愚蠢的人类怎么可能赢过无敌的小魅呢。不服欢迎再战。'
        ][v.value]
        User(session).gain([5, 10000, 0][v.value])
        await send(f'游戏结束！现在棋盘：\n{board}\n{mes}')
