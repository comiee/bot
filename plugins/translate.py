from tools.state import on_message, BaseSession
import aiohttp
import json
import re

src = ''  # 全局变量存储输入语言


async def translate(text, sl='auto', tl='zh'):
    global src
    d = {'中': 'zh', '汉': 'zh', '简': 'zh_CN', '繁': 'zh_TW', '英': 'en', '日': 'ja', '德': 'de', '法': 'fr', '俄': 'ru'}
    url = f'http://translate.google.cn/translate_a/single'
    args = dict(client='gtx', dt='t', dj=1, ie='UTF-8', sl=d.get(sl, sl), tl=d.get(tl, tl), q=text)
    async with aiohttp.ClientSession() as clientSession:
        async with clientSession.get(url, params=args) as resp:
            temp = json.loads(await resp.text())
            src = temp['src']
            return '\n'.join(i['trans'] for i in temp['sentences'])


@on_message
async def _(session: BaseSession):
    msg = session.ctx['raw_message']
    if m := re.match(r'翻译(.*)', msg) or re.match(r'(.*)是什么意思', msg):
        res = await translate(m.group(1))
        if src == 'zh-CN':  # 中译英
            res = await translate(m.group(1), 'auto', 'en')
        await session.send(res)
    elif m := re.match(r'(.*?)[语文]?译(.*?)[语文]? (.*)', msg):
        await session.send(await translate(m.group(3), m.group(1), m.group(2)))
    elif m := re.match(r'(.*)用(.*?)[语文]?怎么说', msg):
        await session.send(await translate(m.group(1), 'auto', m.group(2)))
    elif m := re.match(r'用(.*?)[语文]说(.*)', msg):
        await session.send(await translate(m.group(2), 'auto', m.group(1)))
