from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from tools.User import User
from tools.state import over_mode
from tools.functions import to_int
import re


@on_command('禁言')
@over_mode
async def _(session: CommandSession):
    text = '''\
花费金币禁言对方（使用前请确认小魅是管理员且对方可以被禁言）
1金币可兑换1秒禁言时间
请输入禁言对象（qq或艾特）和禁言时长（单位：秒）：'''
    if session.is_first_run:
        if arg := session.current_arg.strip():
            session.state['arg'] = arg
    arg = re.findall(r'\d+', session.get('arg', prompt=text))
    if len(arg) != 2:
        await session.send('错误输入，命令已取消。')
        return
    target, time = map(int, arg)
    await User(session).ensure_cost(time)
    await session.bot.set_group_ban(
        group_id=session.ctx['group_id'],
        user_id=target,
        duration=time
    )
    await session.send('执行完毕，请自行检查执行结果。')


@on_natural_language('禁言')
async def _(session: NLPSession):
    if match := re.search(r'来([\d〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟億两貮兆]+).*([秒分时天]).*禁言', session.msg):
        time = to_int(match.group(1)) * {'秒': 1, '分': 60, '时': 60 * 60, '天': 60 * 60 * 24}[match.group(2)]
        User(session).gain(time)
        return IntentCommand(80.0, '禁言', current_arg=f'{session.ctx["user_id"]} {time}')
