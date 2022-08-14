from nonebot import on_command, CommandSession
from tools.User import User
from tools.ItemList import ItemList
from adventure.Player import Player


@on_command('金币')
async def _(session: CommandSession):
    user = User(session)
    coin = user.query('coin')
    await session.send(f'{user!r}金币数：{coin}')


@on_command('体力')
async def _(session: CommandSession):
    user = User(session)
    stamina = user.query('stamina')
    await session.send(f'{user!r}体力值：{stamina}')


@on_command('物品', aliases=('背包',))
async def _(session: CommandSession):
    user = User(session)
    items = ItemList(session, f'''
        select name,count,info from inventory inner join item_id on inventory.id=item_id.id where qq={user};
    ''', '物品列表', '名称\t数量\t介绍', 'name,count,info')
    await items.show()


@on_command('装备')
async def _(session: CommandSession):
    user = User(session)
    items = ItemList(session, f'''
        select type_id.info,name,item_id.info from (equipment inner join item_id on equipment.id=item_id.id) 
        inner join type_id on equipment.type=type_id.type where qq={user} and equipment.type>=2 and equipment.type<=10;
    ''', '装备信息', '部位\t名称\t介绍', 'type_name,name,info', 100)
    await session.send(f'{items}\n更换装备请使用“穿戴”“卸下”命令')


@on_command('属性')
async def _(session: CommandSession):
    player = Player(session)
    await session.send(f'''\
人物属性：
血量：{player.hp}/{player.max_hp}
攻击：{player.attack}
防御：{player.defense}''')


@on_command('状态')
async def _(session: CommandSession):
    user = User(session)
    buffs = ItemList(session, f'''
        select name,timestampdiff(second,now(),time),info from effect inner join buff_id on effect.buff=buff_id.buff 
        where qq={user} and time>=now();
    ''', '状态信息', '名称\t剩余时间（秒）\t介绍', 'name,time,info', 10)
    await buffs.show()
