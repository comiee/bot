from nonebot import on_command, CommandSession
from tools.state import is_command
from tools.sql import is_ban
import json
import re
import os
from datetime import datetime

teach_path = 'data/teach.json'
diary_path = 'data/diary.txt'

# 每天将昨天的日记文件名后加日期，然后生成新的日记文件
last_time = datetime.fromtimestamp(os.path.getmtime(diary_path)).strftime('%y%m%d')
if last_time != datetime.now().strftime('%y%m%d'):
    os.rename(diary_path, f'data/diary{last_time}.txt')
if not os.path.exists(diary_path):
    open(diary_path, 'w', encoding='utf-8').close()


@on_command('调教')
async def _(session: CommandSession):
    if is_ban(session):
        await session.send('你已被列入黑名单，无法使用此命令')
        return
    if match := re.search(r'^调教 (.*?)#(.*)$', session.ctx['raw_message'], re.S):
        q, a = match.groups()

        if not q.strip() or not a.strip():
            await session.send('问题或回答为空！')
            return
        if is_command(q.split()[0]):
            await session.send('调教词与原有命令冲突！')
            return
        with open('data/chat.txt', encoding='utf-8') as f:
            for line in f.readlines():
                com = line.split('\t')[0]
                if '%%' not in com and re.search(com, q, re.S):
                    await session.send('调教词与原有模板冲突！')
                    return

        with open(teach_path, 'r', encoding='utf-8') as fin:
            data = json.load(fin)
            if a in data.setdefault(q, []):
                await session.send('小魅已经学会了这个回答了，不用再教了哦。')
                return
            data[q].append(a)
            with open(teach_path, 'w', encoding='utf-8') as fout:
                json.dump(data, fout, ensure_ascii=False)
        with open(diary_path, 'a', encoding='utf-8') as fh:
            fh.write(repr(f'{session.ctx.get("group_id")}@{session.ctx["user_id"]}:{q}#{a}') + '\n')
        await session.send('小魅记住了！')
    else:
        await session.send('请使用正确的指令调教。正确指令：\n调教 问题#回答\n（严禁灌输无用、骂人内容，违者剥夺调教权利终身！）')


@on_command('日记', aliases=('调教日记',))
async def _(session: CommandSession):
    with open(diary_path, 'r', encoding='utf-8') as fh:
        history = [eval(i.strip()) for i in fh.readlines()]
        if arg := session.current_arg.strip():
            if re.search(r'\D', arg):
                l, r = map(int, re.split(r'\D+', arg))
            else:
                l, r = [int(arg)] * 2
            await session.send(f'{l}~{r}次调教记录如下：\n' + '\n'.join(history[l:r + 1]))
        else:
            n = min(len(history), 10)
            await session.send(f'今日小魅共被调教{len(history)}次，近{n}次调教记录如下：\n' + '\n'.join(history[-n:]))
