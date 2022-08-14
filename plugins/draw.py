from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from tools.state import conversation, broadcast, is_sure
from tools.User import User
from adventure.Player import Player
import random
from functools import partial, reduce


@on_command('抽奖')
@conversation
async def draw(session: CommandSession):
    user = User(session)
    send = partial(session.send, at_sender=True)
    text = user + '''\
花费1体力和1金币进行1次抽奖，概率获得以下物品：
4金币（10%）
2金币（20%）
1金币（30%)
0金币（40%）
请输入抽奖次数：'''
    if session.is_first_run and session.current_arg_text.strip():
        count = session.current_arg_text.strip()
    else:
        count = yield text
    try:
        count = int(count)
        assert 1 <= count
    except:
        await send('错误的次数，命令已取消。')
    else:
        await user.ensure_cost(count, 'stamina')
        if user.cost(count):
            result = random.choices([4, 2, 1, 0], [0.1, 0.2, 0.3, 0.4], k=count)
            user.gain(sum(result))
            await send(f'''\
已消耗{count}体力和{count}金币进行{count}次抽奖。
抽奖结果如下，欢迎下次再来。
{result}
共{sum(result)}金币''')
        else:
            user.gain(count, 'stamina')
            await send('余额不足！\n签到和玩游戏可以获得金币哦。')


@on_natural_language('抽奖')
async def _(session: NLPSession):
    arg = session.msg_text[2:]
    if arg.isdigit():
        return IntentCommand(90.0, '抽奖', current_arg=arg)


@on_command('俄罗斯转盘')
@conversation
async def _(session: CommandSession):
    player = Player(session)
    send = partial(session.send, at_sender=True)
    if not player.alive:
        await send('你已经死亡，无法参加此游戏，请复活后再试。')
        return
    answer = yield f'''\
游戏规则：
初始筹码为2金币，转盘中共有1~6六个数字。
每次操作都会使筹码翻倍，然后从转盘剩余数字中抽走一个数字（不放回），
若抽走的数字为6，游戏结束，玩家需要支付筹码；
若抽走的数字不为6，玩家可以选择继续游戏或者带着现有的筹码离开。
抽光所有的非6数字后奖励将升值为100金币。
选择继续将花费10体力开始游戏，
{player!r}继续还是退出？'''
    if not is_sure(answer):
        await send('已放弃游戏')
        return
    await player.ensure_cost(10, 'stamina')
    chip = 2
    nums = [1, 2, 3, 4, 5, 6]
    while 1:
        chip *= 2
        num = random.choice(nums)
        nums.remove(num)
        if num == 6:
            await send(f'很不幸，你抽中了6，赌场老板从你这里收取了{chip}金币')
            if not player.cost(chip):
                player.die()
                await send('由于无法支付筹码，被赌场老板活活打死！\n小魅在这里提醒大家，进入赌场前请先确认自己带有充足的金币哦')
            return
        else:
            if len(nums) == 1:
                player.gain(100)
                await send(f'抽中的数字为{num}，恭喜获得大奖100金币！')
                return
            answer = yield f'{player!r}抽中的数字为{num}，转盘剩余数字为{nums}，当前筹码为{chip}\n继续还是退出？'
            while 1:
                if answer in {'是', '继续', 'Y', 'y', 'yes', '确认'}:
                    break
                elif answer in {'否', '退出', 'N', 'n', 'no', '取消'}:
                    player.gain(chip)
                    await send(f'选择了见好就收，带着{chip}金币离开了')
                    return
                else:
                    answer = yield f'{player!r}错误的选项，请说“继续”或“退出”'


@on_command('老虎机')
@conversation
async def _(session: CommandSession):
    user = User(session)
    jackpot = User(0)
    send = partial(session.send, at_sender=True)
    text = f'''{user!r}\
游戏规则：
每次游戏需押注10个以上的金币。随机抽取三个整数，按以下规则收益：
若为666，获得奖池中所有金币；若有3个数相同，获得赌注的10倍；若有2个数相同，获得赌注的2倍；若为连续三个数字，获得赌注的3倍；若全为奇数或全为偶数，返还赌注。
（若奖池中金币不足，则获取奖池全部金币）。
现在奖池金币数：{jackpot.query()}，你拥有的金币数：{user.query()}。
请输入赌注：'''
    if session.is_first_run and session.current_arg_text.strip():
        count = session.current_arg_text.strip()
    else:
        count = yield text
    try:
        count = int(count)
        assert 10 <= count
    except:
        await send('错误的赌注数量，命令已取消。')
    else:
        await user.ensure_cost(count)
        jackpot.gain(count)
        result = '%03d' % random.randint(0, 999)
        # 判断是否是666
        if result == '666':
            n = jackpot.query()
            assert jackpot.cost(n)
            user.gain(n)
            await send(f'恭喜抽中666！获取奖池剩余金币共{n}。')
            group = f'尾号{str(session.ctx.get("group_id"))[-4:]}的群' if session.ctx['message_type'] == 'group' else '私聊'
            await broadcast(f'恭喜qq尾号{str(user)[-4:]}的用户在{group}中抽中老虎机的666大奖，获得奖金{n}金币！')
        # 判断是否有相同数字
        elif (length := len(set(result))) < 3:
            n = min(count * [0, 10, 2][length], jackpot.query())
            assert jackpot.cost(n)
            user.gain(n)
            await send(f'你抽中的结果为{result}，恭喜获得{n}金币！')
        # 判断是否为连续数字
        elif reduce(lambda a, b: [10, b][b - a == 1], sorted(map(int, result))) != 10:
            n = min(count * 3, jackpot.query())
            assert jackpot.cost(n)
            user.gain(n)
            await send(f'你抽中的结果为{result},恭喜获得{n}金币！')
        # 判断是否全奇全偶
        elif all(map(lambda x: int(x) & 1, result)) or not any(map(lambda x: int(x) & 1, result)):
            assert jackpot.cost(count)
            user.gain(count)
            await send(f'你抽中的结果为{result},恭喜获得{count}金币！')
        # 什么都没中的情况
        else:
            await send(f'你抽中的结果为{result}，赌注已存入奖池，欢迎下次再来。')
        if (n := jackpot.query()) < 1000:
            jackpot.gain(1000 - n)
            await session.send('奖池金币不足1000，已将奖池金币补至1000')


@on_natural_language('老虎机')
async def _(session: NLPSession):
    arg = session.msg_text[3:]
    if arg.isdigit():
        return IntentCommand(90.0, '老虎机', current_arg=arg)
