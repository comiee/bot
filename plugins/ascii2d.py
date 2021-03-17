from nonebot import on_command, CommandSession
import aiohttp
from lxml import etree


@on_command('识图')
async def _(session: CommandSession):
    for i in session.ctx['message']:
        if i['type'] == 'image':
            session.state['url'] = i['data']['url']
            break
    else:
        session.pause('未发现图片，等待输入中')

    url = session.state['url']
    async with aiohttp.ClientSession() as clientSession:
        async with clientSession.get('https://www.ascii2d.net/search/url/' + url) as resp:
            html = etree.HTML(await resp.text(encoding='utf-8'))
            items = html.xpath('//*[@class="detail-box gray-link"]/h6')
            res = ''
            for i in items[:3]:
                for a in i.xpath('./a'):
                    res += f'{a.text}({a.get("href")})\n'
                res += '\n'
            await session.send('找到以下结果：\n' + res)
