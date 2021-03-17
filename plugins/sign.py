from nonebot import on_command, CommandSession
from tools.sql import cur


@on_command('签到')
async def _(session: CommandSession):
    user = session.ctx['user_id']
    if cur.execute(f'select * from info where qq={user} and date=curdate();'):
        await session.send('你今天已经签到过了，明天再来吧。', at_sender=True)
    else:
        cur.execute(f'''
            insert into info(qq,coin,date,stamina) values({user},3,curdate(),200) 
            on duplicate key update coin=coin+3,date=curdate(),stamina=greatest(stamina,200);
        ''')
        cur.execute(f'select coin from info where qq={user}')
        await session.send('签到成功，金币+3，体力恢复为200，当前金币%d' % cur.fetchone(), at_sender=True)
