from nonebot import on_command, CommandSession, MessageSegment, on_natural_language, NLPSession, IntentCommand
from tools.state import conversation, when
from tools.User import User
from tools.functions import to_int
import aiohttp
import json
import qrcode
import os
import re
import requests
import threading
from PIL import Image
from io import BytesIO

user_filter = when(
    {'group_id': {694541980, 811912656, 324085758,  272943085}},
    {'message_type': 'private', 'user_id': {1440667228, 2667336028, 1192916519}}
)


def img_save(url):  # 从url保存图片
    resp = requests.get(url)
    img = Image.open(BytesIO(resp.content))
    name = re.search(r'^.*/(.*)$', url).group(1)
    img.save('data/pic/' + name)


@on_command('色图')
@user_filter
@conversation
async def h_pic(session: CommandSession):
    user = User(session)
    keyword = session.state['keyword']
    num = session.state['num']
    r18 = session.state['r18']
    coin = 15 + 5 * r18  # 底价
    r18 = {0: 0, 1: 2, 2: 1}[r18]  # r18等级改为api的格式
    url = 'https://api.lolicon.app/setu'
    args = dict(keyword=keyword, num=num, r18=r18)
    if keyword:
        coin += 10
    coin *= num
    yield f'''\
收费规则：底价15金币，指定关键字额外花费10金币，色图等级每级5金币（共 0 1 2 三个等级，默认为等级1）。
{user!r}本次操作将花费{coin}金币，是否继续？'''
    await user.ask()
    if user.query() < coin:
        await session.send('余额不足！\n签到和玩游戏可以获得金币哦。')
        return
    await session.send('正在爬取，请稍候。')
    try:
        async with aiohttp.ClientSession() as clientSession:
            async with clientSession.get(url, params=args) as resp:
                temp = json.loads(await resp.text())
                count = temp['count']
                coin_res = coin // num * count
                assert user.cost(coin_res)  # 实际扣钱的个数是找到的数量
                for res in temp['data']:
                    url = res['url']
                    await session.send(url[8:15] + '\n' + url[15:])
                    threading.Thread(target=img_save, args=(url,)).start()
                    # await session.send(MessageSegment.image(url))
                    img = qrcode.make(data=url)
                    img.save('temp.jpg')
                    await session.send(MessageSegment.image(os.getcwd() + r'\temp.jpg'))
                    os.remove('temp.jpg')
                text = f'已找到{count}个结果'
                if coin != coin_res:
                    text += f'，实际花费{coin_res}金币,已退还{coin - coin_res}金币'
                    await session.send(text)
                elif num > 1:
                    await session.send(text)
    except:
        await session.send('爬取失败，金币已返还。')


@h_pic.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        session_args = session.current_arg_text.strip().split()  # 被自然语言处理器处理过之后不会留有current_arg_text

        def f(num=1, keyword='', r18=1):
            num = to_int(num)
            r18 = to_int(r18)
            assert 1 <= num <= 100
            assert 0 <= r18 <= 2
            session.state['num'] = num
            session.state['keyword'] = keyword
            session.state['r18'] = r18

        try:
            d = {'数量': 'num', '关键字': 'keyword', 'r18等级': 'r18'}
            d.update(dict(zip(d.values(), d.values())))
            args = []
            kwargs = {}
            for arg in session_args:
                if '=' in arg:
                    k, v = arg.split('=')
                    kwargs[d[k]] = v
                else:
                    args.append(arg)
            f(*args, **kwargs, **session.state)  # 传入state，同时处理自然语言处理器的结果
        except:
            await session.send('''\
参数格式或数据错误，正确的参数格式为 色图 [数量] [关键字] [r18等级]
其中数量的范围是1~100，r18等级的范围是0~2''')
            session.finish()


@on_natural_language('色图')
@user_filter
async def _(session: NLPSession):
    args = {}
    if match := re.search(r'来点(.*)色图', session.msg):
        args['keyword'] = match.group(1)
        return IntentCommand(90.0, '色图', args=args)
    if match := re.search(r'来([\d\-负〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟億两貮兆]*)张(.*)色图', session.msg):
        if match.group(1):
            args['num'] = to_int(match.group(1))
        else:
            args['num'] = 1
        if match.group(2):
            args['keyword'] = match.group(2)
        if args['num'] > 100:
            await session.send('你要的太多了，小心樯橹灰飞烟灭哦')
        elif args['num'] <= 0:
            await session.send('不买就不要来打扰我，我可是很忙的')
        else:
            return IntentCommand(90.0, '色图', args=args)


@on_command('色图盲盒')
@user_filter
async def _(session: CommandSession):
    url = 'http://iw233.cn/api/Random.php'
    async with aiohttp.ClientSession() as clientSession:
        async with clientSession.get(url) as resp:
            await session.send(MessageSegment.image(str(resp.url)))
