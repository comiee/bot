from nonebot import on_command, CommandSession, get_bot, scheduler
from tools.state import on_message, BaseSession, broadcast
from functools import wraps
from datetime import datetime, timedelta
import json
import os
import time
import re
from threading import Thread

path = 'data/record.json'
log_path = 'data/log.txt'

bot = get_bot()
_send = bot.send


@wraps(_send)
async def send(context, message, **kwargs):
    await _send(context, message, **kwargs)

    if os.path.exists(path):
        with open(path, 'r') as fin:
            record = json.load(fin)
    else:
        record = {}
    record_self_id = record.setdefault(str(context['self_id']), {})
    today = datetime.now().strftime('%Y-%m-%d')
    record_self_id[today] = record_self_id.get(today, 0) + 1

    if len(record_self_id) > 7:
        record_self_id.pop(sorted(record_self_id)[0])

    with open(path, 'w') as fout:
        json.dump(record, fout)

    with open(log_path, 'a+', encoding='utf-8') as f:
        f.write(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]') + repr(message) + '\n')


bot.send = send


@on_command('次数')
async def _(session: CommandSession):
    with open(path, 'r') as f:
        record = json.load(f)
        await session.send('小魅近期发言次数如下：\n' +
                           '\n'.join(map('%s：发言%d条。'.__mod__, record[str(session.ctx['self_id'])].items())))


@on_message
async def _(session: BaseSession):
    with open(log_path, 'a+', encoding='utf-8') as f:
        f.write(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]') +
                f'{session.ctx.get("group_id")}@{session.ctx["user_id"]}:{session.ctx["raw_message"]!r}\n')


@bot.server_app.before_websocket
async def _():
    @scheduler.scheduled_job('date', run_date=datetime.now() + timedelta(seconds=1))
    async def _():
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as fi:
                lines = fi.readlines()
            if not lines:
                return
            if m := re.match(r'\[.*?\]', lines[-1]):
                a = datetime.strptime(m.group(), '[%Y-%m-%d %H:%M:%S]')
                b = datetime.now()
                s = int((b - a).total_seconds())
                if s < 60 * 10:  # 10分钟
                    msg = ''
                elif s < 60 * 60:  # 1小时
                    msg = '小魅休眠了一小段时间，看来主人的电脑又出故障了呢'
                elif s < 60 * 60 * 8:  # 8小时
                    msg = f'大家好，小魅起床了，可以继续为大家服务了。这次小魅只睡了{s // 3600}小时{s % 3600 // 60}分钟，有点困呢'
                elif s < 60 * 60 * 24:  # 24小时
                    msg = f'元气少女小魅起床！这次小魅睡了整整{s // 3600}小时{s % 3600 // 60}分钟！，现在小魅精神满满！'
                else:
                    msg = f'距离上次醒来已经过去了{s // 86400}天{s % 86400 // 3600}小时，休眠的时间太长让人感觉很寂寞呢'
                for group_id in [694541980, 811912656, 324085758]:
                    await bot.send_group_msg(group_id=group_id, message=msg)
            with open(log_path, 'w', encoding='utf-8') as fo:
                fo.writelines(lines[-100:])
