from nonebot import on_command, CommandSession, permission
from tools.sql import cur
from tools.state import mode, conversation, broadcast
from tools.User import User
from functools import partial
import re
import sys
import os

super_command = partial(on_command, permission=permission.SUPERUSER)


@super_command('on')
async def _(session: CommandSession):
    if mode[session] == 'chat':
        await session.send('聊天功能已经是开启状态了哦。')
    else:
        mode[session] = 'chat'
        await session.send('聊天功能已开启，快来和我聊天吧！')


@super_command('off')
async def _(session: CommandSession):
    if mode[session] == 'chat':
        mode[session] = ''
        await session.send('聊天功能已关闭。')
    else:
        await session.send('我已经闭嘴了，你还要我怎样？')


@super_command('at')
@conversation
async def _(session):
    text = yield '帮艾特小冰模式启动！'
    while text != 'over':
        text = yield '[CQ:at,qq=2854196306] ' + text
    await session.send('帮艾特小冰模式关闭！')


@super_command('ban')
async def _(session: CommandSession):
    if qq := session.current_arg_text.strip():
        if cur.execute(f'select * from ban where qq={qq};'):
            await session.send('这名用户已经在黑名单里了。')
        else:
            cur.execute(f'insert into ban(qq) values({qq});')
            await session.send('添加黑名单成功。')


@super_command('unban')
async def _(session: CommandSession):
    if qq := session.current_arg_text.strip():
        if cur.execute(f'select * from ban where qq={qq};'):
            cur.execute(f'delete from ban where qq={qq};')
            await session.send('移除黑名单成功。')
        else:
            await session.send('这名用户并不在黑名单里。')


@super_command('gain')
async def _(session: CommandSession):
    qq, count = re.findall(r'-?\d+', session.current_arg)
    User(qq).gain(count)
    await session.send('完成！')


@super_command('broadcast')
async def _(session: CommandSession):
    success, fail = await broadcast(session.current_arg)
    await session.send(f'广播已发送！{success}个群成功，{fail}个群失败。')


@super_command('exec')
async def _(session: CommandSession):
    exec('async def func(session,User):\n\t' + session.current_arg_text.replace('\n', '\n\t'))
    await eval('func(session,User)')


@super_command('eval')
async def _(session: CommandSession):
    await session.send(str(eval(session.current_arg_text)))


@super_command('sql')
async def _(session: CommandSession):
    cur.execute(session.current_arg_text)
    await session.send('\t'.join(next(zip(*cur.description))) + '\n' + \
                       '\n'.join('\t'.join(map(str, i)) for i in cur.fetchall()))


@super_command('cmd')
async def _(session: CommandSession):
    with os.popen(session.current_arg_text) as p:
        await session.send(p.read())


@super_command('小魅，睡觉了', aliases=('小魅，关机',))
async def _(session: CommandSession):
    for group_id in [694541980, 811912656, 324085758]:
        await session.bot.send_group_msg(group_id=group_id, message='小魅要去陪主人睡觉了，大家晚安')
    if session.ctx['raw_message'] == '小魅，关机':
        os.system('shutdown -s -t 0')
    sys.exit()
