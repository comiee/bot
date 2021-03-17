from nonebot import on_command, CommandSession, _bot
from functools import wraps
from datetime import datetime
import json
import os
import time
from win10toast import ToastNotifier
from threading import Thread

path = 'data/record.json'
_send = _bot.send


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
    if record_self_id[today] > 1800:
        await _send(context, '今日次数已达上限，为防止被封，小魅将进入休眠，大家明天见！')
        Thread(target=lambda: ToastNotifier().show_toast('小魅', '小魅休息了', 'mei.ico', 86400), daemon=True).start()
        time.sleep(5)
        exit()

    with open(path, 'w') as fout:
        json.dump(record, fout)


_bot.send = send


@on_command('次数')
async def _(session: CommandSession):
    with open(path, 'r') as f:
        record = json.load(f)
        await session.send('小魅近期发言次数如下：\n' +
                           '\n'.join(map('%s：发言%d条。'.__mod__, record[str(session.ctx['self_id'])].items())))
