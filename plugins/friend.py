from nonebot import on_command, CommandSession, on_request, RequestSession
from tools.state import conversation, get_user, in_private
import re


@on_request('friend')
async def _(session: RequestSession):
    await session.approve()
    await session.send('欢迎添加小魅机器人为好友')


@on_request('group')
async def _(session: RequestSession):
    await session.approve()
    await session.send(f'[CQ:at,qq={get_user(session)}] 欢迎新人')
    if session.ctx['group_id'] == 694541980:
        name = re.search(r'答案：(.*)$', session.ctx['comment']).group(1)
        await session.bot.set_group_card(**session.ctx, card=name)


@on_command('反馈', aliases=('联系主人',))
@in_private
@conversation
async def _(session: CommandSession):
    question = yield '''\
您好，是遇到什么问题了吗？我可以帮你转告给我的主人哦。
（通过此渠道骚扰主人将被拉黑）
请详细描述你的问题（输入“取消”可取消本次命令）：'''
    if question == '取消':
        await session.send('命令已取消。')
        return
    await session.bot.send_private_msg(user_id=1440667228, message=f'来自{get_user(session)}的反馈：\n{question}')
    await session.send('问题已经报告给主人了，请耐心等待回复哦。')
