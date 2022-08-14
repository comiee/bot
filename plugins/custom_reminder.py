from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand, scheduler, get_bot
from tools.state import conversation, is_friend
from nonebot.session import BaseSession
from tools.functions import analyse_time
from tools.User import User
from comiee import JsonFile
from datetime import datetime
from collections import defaultdict
import re


async def analyse(session: BaseSession, s: str):
    """解析时间文本的函数"""
    try:
        res = analyse_time(s)
        assert res
    except ValueError as e:
        await session.send(f'解析时间出错：{e.args[0]}')
        raise
    except AssertionError:
        await session.send('无法解析的时间格式')
        raise
    return res


class Reminder(JsonFile, defaultdict):  # {用户qq:{时间:提醒内容,}}
    def __init__(self, filename):
        JsonFile.__init__(self, filename)
        defaultdict.__init__(self, dict)
        temp = []
        for qq, d in self.items():
            for s, text in d.items():
                time = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                if time > datetime.now():
                    self.register(qq, time, text)
                else:
                    temp.append((qq, s))
        for qq, s in temp:
            del self[qq][s]
            if not self[qq]:
                del self[qq]
        self.update()

    def __getitem__(self, item):
        return super().__getitem__(str(item))

    def __setitem__(self, key, value):
        super().__setitem__(str(key), value)

    def register(self, qq, time, text):
        s = time.strftime('%Y-%m-%d %H:%M:%S')
        self[qq][s] = text
        self.update()

        @scheduler.scheduled_job('date', id=f'{qq} {s}', run_date=time)
        async def _():
            await get_bot().send_private_msg(user_id=qq, message='您的自定义提醒：\n' + text)
            del self[qq][s]
            self.update()


reminder = Reminder('data/custom_reminder.json')


@on_command('添加提醒', aliases=('新增提醒', '新建提醒', '自定义提醒'))
@conversation
async def _(session: CommandSession):
    user = User(session)
    if not await is_friend(user):
        await session.send('使用此功能前请先加小魅为好友')
        return
    if len(reminder[user]) >= 9:
        await session.send('每个人最多只能设置9条自定义提醒，请先删除提醒或者等待提醒结束再试')
        return
    args = session.current_arg_text.split(' ', 2)
    if len(args) < 2:
        await session.send('命令格式错误，正确格式：\n添加提醒 [时间] [内容]')
        return
    t = await analyse(session, args[0])
    yield f'将于{t}提醒您{args[1]}，是否确认？'
    await user.ask()
    reminder.register(user, t, args[1])
    await session.send('提醒添加成功。')


@on_natural_language('提醒我')
async def _(session: NLPSession):
    m = re.search(r'(.*)提醒我(.*)', session.msg)
    return IntentCommand(80.0, '添加提醒', current_arg=m.group(1) + ' ' + m.group(2))


@on_command('删除提醒', aliases=('取消提醒',))
@conversation
async def _(session: CommandSession):
    user = User(session)
    arr = list(reminder[user])
    index = yield '您设置的自定义提醒如下，请回复要删除的提醒编号\n' + \
                  '\n'.join(f'{i + 1}、{k}  {reminder[user][k]}' for i, k in enumerate(arr))
    try:
        index = int(index) - 1
        assert 0 < index <= len(arr)
    except:
        await session.send('输入的编号有误，命令已取消。')
        return
    scheduler.remove_job(f'{user} {arr[index]}')
    del reminder[user][arr[index]]
    await session.send('提醒删除成功。')


@on_command('提醒列表', aliases=('自定义提醒列表',))
async def _(session: CommandSession):
    user = User(session)
    await session.send('您设置的自定义提醒如下：\n' + \
                       '\n'.join(f'{k}  {v}' for k, v in reminder[user].items()))


@on_natural_language('')
async def _(session: NLPSession):
    if m := re.search('(.*)是(什么时间|什么时候|什么日子|几点|几号|哪天|哪一天)', session.msg):
        if m.group(1) == '现在':
            await session.send(f'现在是{datetime.now()}')
            return
        t = await analyse(session, m.group(1))
        await session.send(f'{m.group(1)}是{t}')
