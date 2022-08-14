from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from tools.state import conversation
from tools.functions import to_int
import aiohttp
import re
from lxml import etree


@on_command('百科')
@conversation
async def _(session: CommandSession):
    question = session.current_arg_text
    async with aiohttp.ClientSession() as clientSession:
        url = 'https://baike.baidu.com/item/' + question
        for i in range(2):  # for是为了处理多义词，理论来讲不会执行第三次，保险起见用range(2)
            async with clientSession.get(url, params={'force': 1}) as resp:
                html = etree.HTML(await resp.text(encoding='utf-8'))
                result = []
                for element in html.xpath('//*[@class="lemma-summary"]/*'):
                    result.append(''.join(element.xpath('descendant-or-self::text()')))
            if result:  # 如果已经找到了结果，则退出循环，否则开始判断是不是多义词条
                break
            ul_list = html.xpath('//ul[@class="custom_dot  para-list list-paddingleft-1"]')
            if not ul_list:  # 不是多义词条，退出程序
                await session.send('未找到相关内容。')
                return
            ul = ul_list[0]
            text_list = ul.xpath('.//text()')
            href_list = ul.xpath('.//@href')
            list_text = '\n'.join(f'{i}:{e}' for i, e in enumerate(text_list, 1))
            temp = yield f'{question}是个多义词，请回复序号查看对应词条：\n{list_text}'
            if 0 < (n := to_int(temp)) <= len(text_list):
                url += '/' + href_list[n - 1].split('/')[-1]  # 更新url之后回到for开始的地方
            else:
                await session.send('输入错误，命令已取消。')
                return
        result.append('————来自百度百科')
        await session.send('\n'.join(result))


@on_natural_language('是')
async def _(session: NLPSession):
    if re.search(r'[这那哪个你我他她它]|(主人)', session.msg):
        return
    if match := re.search(r'^什么是(.*)|(.*)是什么$|^谁是(.*)|(.*)是谁$', session.msg):
        return IntentCommand(60.0, '百科', current_arg=next(filter(bool, match.groups())))
