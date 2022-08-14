"""共用的数据和函数"""

from nonebot import _bot, on_command, on_natural_language
from nonebot.command import CommandManager, _FinishException
from nonebot.session import BaseSession
from tools.sql import get_user
from collections import defaultdict
from functools import wraps
from itertools import chain


def get_id(session):
    """获取群号，如果没有就获取qq号"""
    return session.ctx.get('group_id', session.ctx['user_id'])


def is_command(cmd: str):
    """判断是不是已有命令"""
    for i in chain(*CommandManager._commands, CommandManager._aliases):
        if cmd.split()[0] == i:
            return True
    return False


def is_sure(s):
    """判断用户回答是肯定还是否定"""
    return s in {'是', '继续', 'Y', 'y', 'yes', '确认'}


async def is_friend(user):
    """判断此人是不是好友"""
    for friend in await _bot.get_friend_list():
        if user == friend['user_id']:
            return True
    return False


async def broadcast(msg):
    """广播到所有群"""
    success, fail = 0, 0
    for group in await _bot.get_group_list():
        try:
            await _bot.send_group_msg(group_id=group['group_id'], message=msg)
            success += 1
        except:
            fail += 1
    return success, fail


def on_message(func):
    """重封装on_message"""

    @_bot.on_message
    @wraps(func)
    async def wrapper(message):
        await func(BaseSession(_bot, message))

    return wrapper


def on_mode(mode_name):
    """只在此模式运行"""

    def get_func(func):
        @wraps(func)
        async def wrapper(session):
            text = session.ctx['raw_message']
            if mode[session] != mode_name \
                    or not power[session] \
                    or not text.strip() \
                    or text[0] == '%' \
                    or is_command(text):
                return
            else:
                return await func(session)

        return wrapper

    return get_func


class ModeSwitch:
    """模式切换"""

    # 命令名->模式名->执行函数。提供同一结束命令可以结束多个模式的功能
    ends = defaultdict(lambda: defaultdict(lambda: lambda _: ...))

    def __init__(self, mode_name, begin_cmd, end_cmd='不玩了', end_str='本来就没有在玩啊。'):
        self.mode_name = mode_name
        self.begin_cmd = begin_cmd
        self.end_cmd = end_cmd
        self.end_str = end_str

    def __call__(self, begin_func):
        """模式开始命令"""

        @on_command(self.begin_cmd)
        @wraps(begin_func)
        async def _(session):
            if mode[session] not in {'chat', ''}:
                await session.send('现在正在游戏中，无法执行此命令。')
                return
            else:
                last[session], mode[session] = mode[session], self.mode_name
                await begin_func(session)

        return self

    def end(self, end_func):
        """模式结束命令"""

        @wraps(end_func)
        async def wrapper(session):
            mode[session] = last[session]
            del last[session]
            await end_func(session)

        if not ModeSwitch.ends[self.end_cmd]:
            @on_command(self.end_cmd)
            async def _(session):
                if mode[session] in ModeSwitch.ends[self.end_cmd]:
                    await ModeSwitch.ends[self.end_cmd][mode[session]](session)
                else:
                    await session.send(self.end_str)
        ModeSwitch.ends[self.end_cmd][self.mode_name] = wrapper

    def run(self, run_func):
        """模式中运行"""

        @on_natural_language
        @on_mode(self.mode_name)
        @wraps(run_func)
        async def _(session):
            return await run_func(session)


def over_mode(func):
    """执行时关闭聊天功能"""

    @wraps(func)
    async def wrapper(session):
        power[session] = False
        try:
            result = await func(session)
        except _FinishException as e:
            result = e.result
        power[session] = True
        return result

    return wrapper


def conversation(func):
    """用于对话"""

    @over_mode
    @wraps(func)
    async def wrapper(session):
        if session.is_first_run:
            session.state['function'] = func(session)
            session.state['question'] = None
            session.state['answer'] = None
        try:
            while 1:
                session.get('answer', prompt=session.state['question'])
                session.state['question'] = await session.state['function'].asend(session.state['answer'])
                del session.state['answer']
        except StopAsyncIteration:
            return

    return wrapper


class InSessionMeta(type):
    def __call__(cls, session, *args, key=None, **kwargs):
        if key is None:
            key = cls.__name__
        if key not in session.state:
            session.state[key] = super().__call__(session, *args, **kwargs)
        return session.state[key]


class InSession(metaclass=InSessionMeta):
    """此类的子类在同一个session中不会重复创建实例"""

    def __init__(self, session):
        self.session = session

    def __del__(self):
        name = type(self).__name__
        if name in self.session.state:
            del self.session.state[name]


def when(*conditions, black_list=False, message=None):
    """符合条件时执行，同一个condition中为且，不同condition为或。black_list：黑名单模式。message：条件不符合时发送的消息"""

    def get_func(func):
        @wraps(func)
        async def wrapper(session):
            for condition in conditions:
                for k, v in condition.items():
                    if not isinstance(v, (set, list, tuple)):
                        condition[k] = {v}
                    if (session.ctx.get(k, None) not in condition[k]) ^ black_list:
                        break
                else:
                    return await func(session)
            if message:
                await session.send(message)

        return wrapper

    return get_func


in_group = when({'message_type': 'group'}, message='请在群聊中使用此功能。')
in_private = when({'message_type': 'private'}, message='请在私聊中使用此功能。')


class State(defaultdict):
    """用于记录信息，除了可以用session进行索引操作外，其他均与defaultdict一致"""

    def __init__(self, default, get_key):
        super().__init__(default)
        self.get_key = lambda key: get_key(key) if isinstance(key, BaseSession) else key

    def __getitem__(self, key):
        return super().__getitem__(self.get_key(key))

    def __setitem__(self, key, value):
        return super().__setitem__(self.get_key(key), value)

    def __delitem__(self, key):
        try:
            return super().__delitem__(self.get_key(key))
        except KeyError:
            pass


mode = State(lambda: '', get_id)  # 当前模式
power = State(lambda: True, get_user)  # 总开关
last = State(lambda: 'chat', get_id)  # 记录上一次的mode
history = State(lambda: ['', 0], get_id)  # 记录上一条消息及其连续出现次数
