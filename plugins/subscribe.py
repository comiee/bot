from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand, scheduler, get_bot
from nonebot.helpers import send_to_superusers
from tools.state import conversation, is_friend
from tools.User import User
from comiee import JsonFile, group
from datetime import datetime, timedelta


def group_bool(it, key):
    """按照it的元素执行key的结果是true还是false来分类，返回二元数组，前一项是true的结果，后一项是false的结果"""
    d = group(it, key)
    return d.get(True, []), d.get(False, [])


data = JsonFile('data/subscribe.json')  # 订阅内容->用户qq的列表
subscribe_list = ['深渊', '剿灭']  # 可订阅的内容
for x in subscribe_list:
    if x not in data:
        data[x] = []
data.update()


@on_command('订阅列表')
@conversation
async def _(session: CommandSession):
    user = User(session)
    if not await is_friend(user):
        await session.send('使用此功能前请先加小魅为好友')
        return
    if not session.current_arg_text:
        answer = yield f'''\
    您已订阅的内容有：
    {[i for i in subscribe_list if user in data[i]]}
    可订阅的内容有：
    {[i for i in subscribe_list if user not in data[i]]}
    请回复项目名切换订阅状态（不同项目用逗号或空格隔开）：'''
    else:
        answer = session.current_arg_text
    names = answer.replace(',', ' ').replace('，', ' ').split(" ")
    c = [i for i in names if i not in data]  # 无效的选项
    names = [i for i in names if i in data]
    for i in names:
        if i not in data:
            c.append(i)
        elif user in data[i]:
            data[i].remove(user)
        else:
            data[i].append(user)
    data.update()
    a = [i for i in names if user in data[i]]  # 订阅
    b = [i for i in names if user not in data[i]]  # 退订
    texts = []
    if a:
        texts.append(f'成功订阅：\n{a}')
    if b:
        texts.append(f'成功退订：\n{b}')
    if c:
        texts.append(f'无效选项：\n{c}')
    if a:
        texts.append('小魅将会通过私聊发送订阅内容')
    elif b:
        texts.append('欢迎下次再来！')
    else:
        texts.append('无操作')
    await session.send('\n'.join(texts))


@on_command('订阅')
@conversation
async def _(session: CommandSession):
    user = User(session)
    if not await is_friend(user):
        await session.send('使用此功能前请先加小魅为好友')
        return
    name = session.current_arg_text
    if not name:
        name = yield f'''\
可订阅项目有：
{[i for i in subscribe_list if user not in data[i]]}
请输入要订阅的项目名称：'''
    if name not in subscribe_list:
        await session.send('不存在的项目名，命令已取消')
    elif user in data[name]:
        await session.send(f'您已订阅项目【{name}】，请勿重复订阅')
    else:
        data[name].append(user)
        data.update()
        await session.send(f'订阅成功，小魅将会通过私聊发送订阅内容')


@on_command('退订')
@conversation
async def _(session: CommandSession):
    user = User(session)
    name = session.current_arg_text
    if not name:
        name = yield f'''\
已订阅项目有：
{[i for i in subscribe_list if user in data[i]]}
请输入要退订的项目名称：'''
    if name not in subscribe_list:
        await session.send('不存在的项目名，命令已取消')
    elif user in data[name]:
        data[name].remove(user)
        data.update()
        await session.send(f'退订成功，欢迎下次再来')
    else:
        await session.send(f'您未订阅此内容，无需退订')


@on_natural_language('提醒')
async def _(session: NLPSession):
    name = session.msg[0:-2]
    if name in subscribe_list:
        return IntentCommand(100.0, '订阅', current_arg=name)


def weekly_subscribe(weekday, hour, minute=0, second=0):
    now = datetime.now()
    sunday = datetime.strptime(now.strftime('%Y %m %d'), '%Y %m %d') - timedelta(now.isoweekday())  # 上一个周日的0点
    target = sunday + timedelta(weekday, hours=hour, minutes=minute, seconds=second)
    if target < now:
        target += timedelta(7)
    return scheduler.scheduled_job('interval', days=7, start_date=target)


async def send_subscribe(name, text):
    temp = []  # 存储发送失败的用户id
    for user in data[name]:
        try:
            await get_bot().send_private_msg(user_id=user, message=text)
        except:
            temp.append(user)
    if temp:
        friend_list = {i['user_id'] for i in await get_bot().get_friend_list()}
        t, f = group_bool(temp, friend_list.__contains__)
        for user in f:
            data[name].remove(user)
        data.update()
        await send_to_superusers(get_bot(), f'''\
    发送{name}提醒时以下用户发送失败：
    是好友的：{t}
    不是好友的：{f}
    已将未加好友的用户从订阅列表中移除''')


@weekly_subscribe(3, 20)
@weekly_subscribe(7, 20)
async def _():
    await send_subscribe('深渊', '您的订阅消息：\n今晚深渊结算，别忘记打哦')


@weekly_subscribe(6, 10)
async def _():
    await send_subscribe('剿灭', '您的订阅消息：\n刀客塔现在还不能休息哦')
