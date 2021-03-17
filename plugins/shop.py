from nonebot import on_command, CommandSession
from tools.state import over_mode
from tools.ItemList import ItemList
from tools.User import User


@on_command('购买', aliases=('商品',))
@over_mode
async def _(session: CommandSession):
    user = User(session)
    commodities = ItemList(session, '''
        select item_id.id,name,price,info from shop inner join item_id on shop.id=item_id.id 
        where price>=0 order by priority desc;
    ''', '商品列表', '编号\t名称\t价格\t介绍', 'id,name,price,info')

    @commodities.get(True, '请输入要购买的物品编号和数量')
    def _(id, count):
        if user.cost(commodities[id].price * count):
            user.give(id, count)
            return '购买成功！'
        else:
            return '余额不足！'

    await commodities.send_result()


@on_command('出售')
@over_mode
async def _(session: CommandSession):
    user = User(session)
    items = ItemList(session, f'''
        select item_id.id,name,count,sell from (shop inner join inventory on shop.id=inventory.id) 
        inner join item_id on shop.id=item_id.id where qq={user} and sell>=0;
    ''', '物品列表', '编号\t名称\t数量\t出售价格', 'id,name,count,sell')

    @items.get(True, '请输入要出售的物品编号和数量')
    def _(id, count):
        if user.remove(id, count):
            user.gain(items[id].sell * count)
            return '出售成功！'
        else:
            return '数量不足！'

    await items.send_result()
