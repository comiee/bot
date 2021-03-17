from nonebot.session import BaseSession
from tools.sql import get_user, cur


class User(int):
    """用户"""

    def __new__(cls, session):
        qq = get_user(session)
        obj = super().__new__(cls, qq)
        obj.at = f'[CQ:at,qq={qq}] '
        obj.session = session
        if isinstance(session, BaseSession):
            obj.isSession = True
            obj.name = session.ctx['sender']['nickname']
            obj.card = session.ctx['sender'].get('card', obj.name) or obj.name
        else:
            obj.isSession = False
            obj.name = str(session)
            obj.card = str(session)
        return obj

    def __add__(self, other):
        if isinstance(other, str):
            return self.at + other
        else:
            return super() + other

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return self.at

    def gain(self, n, currency='coin', base='info'):
        """给钱"""
        user = int(self)
        cur.execute(f'''
            insert into {base}(qq,{currency}) values({user},{n}) on duplicate key update {currency}={currency}+{n};
        ''')
        return True

    def cost(self, n, currency='coin', base='info'):
        """扣钱，返回是否成功"""
        user = int(self)
        if cur.execute(f'select * from {base} where qq={user} and {currency}>={n};'):
            cur.execute(f'update info set {currency}={currency}-{n} where qq={user};')
            return True
        else:
            return False

    def query(self, currency='coin', base='info', default=0):
        """查钱"""
        user = int(self)
        if cur.execute(f'select {currency} from {base} where qq={user};'):
            return cur.fetchone()[0]
        else:
            return default

    def give(self, id, count):
        """给予物品"""
        user = int(self)
        cur.execute(f'''
            insert into inventory(qq,id,count) values({user},{id},{count}) on duplicate key update count=count+{count};
        ''')

    def remove(self, id, count):
        """移除物品"""
        user = int(self)
        if cur.execute(f'select * from inventory where qq={user} and id={id} and count>={count};'):
            cur.execute(f'update inventory set count=count-{count} where qq={user} and id={id};')
            cur.execute('delete from inventory where count<=0;')
            return True
        else:
            return False

    def add_buff(self, buff, time):
        """加buff"""
        user = int(self)
        cur.execute(f'delete from effect where time<=now();')
        cur.execute(f'''
            insert into effect(qq,buff,time) values({user},{buff},now()+interval {time} second) 
            on duplicate key update time=time+interval {time} second;
        ''')

    def sub_buff(self, buff=None):
        """减buff"""
        user = int(self)
        if buff:
            cur.execute(f'delete from effect where qq={user} and buff={buff};')
        else:
            cur.execute(f'delete from effect where qq={user};')

    async def ask(self, prompt=None):
        """询问是否继续"""
        if self.session.get('answer', prompt=prompt) not in {'是', '继续', 'Y', 'y', 'yes', '确认'}:
            await self.session.send('命令已取消。', at_sender=True)
            self.session.finish()

    async def ensure_cost(self, n, currency='coin', base='info'):
        """确保扣钱"""
        tips = {
            'coin': '余额不足！\n签到和玩游戏可以获得金币哦。',
            'stamina': '体力不足！\n签到可以获得体力哦。',
        }
        if not self.cost(n, currency, base):
            await self.session.send(tips[currency])
            self.session.finish()

    async def is_group_member(self, session):
        """判断是否是某群的成员"""
        member_list = await session.bot.get_group_member_list(**session.ctx)
        id_list = {i['user_id'] for i in member_list}
        return self in id_list
