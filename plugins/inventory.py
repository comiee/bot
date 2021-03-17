from nonebot import on_command, CommandSession
from tools.sql import cur
from tools.state import over_mode
from tools.ItemList import ItemList
from tools.User import User


@on_command('穿戴')
@over_mode
async def _(session: CommandSession):
    user = User(session)
    items = ItemList(session, f'''
        select item_id.id,name,count,info,type from inventory inner join item_id on inventory.id=item_id.id 
        where qq={user} and type>=2 and type<=10;
    ''', '装备列表', '编号\t名称\t数量\t介绍', 'id,name,count,info,type')

    @items.get(False, '请输入要装备的物品编号')
    def _(id, _):
        type_id = items[id].type
        if cur.execute(f'select id from equipment where qq={user} and type={type_id} and id!=0;'):
            user.give(cur.fetchone()[0], 1)
        cur.execute(f'insert into equipment(qq,type,id) values({user},{type_id},{id}) on duplicate key update id={id};')
        assert user.remove(id, 1)
        return '穿戴成功！'

    await items.send_result()


@on_command('卸下')
@over_mode
async def _(session: CommandSession):
    user = User(session)
    items = ItemList(session, f'''
        select type_id.type,type_id.info,name,item_id.id from 
        (equipment inner join item_id on equipment.id=item_id.id) inner join type_id on equipment.type=type_id.type 
        where qq={user} and equipment.type>=2 and equipment.type<=10;
    ''', '装备信息', '编号\t部位\t名称', 'type_id,type_name,name,id')

    @items.get(False, '请输入要卸下的装备编号')
    def _(type_id, _):
        cur.execute(f'delete from equipment where qq={user} and type={type_id}')
        user.give(items[type_id].id, 1)
        return '卸装成功！'

    await items.send_result()


@on_command('使用')
@over_mode
async def _(session: CommandSession):
    user = User(session)
    items = ItemList(session, f'''
        select item_id.id,name,count,info,nbt from inventory inner join item_id on inventory.id=item_id.id 
        where qq={user} and type=1;
    ''', '可使用物品列表', '编号\t名称\t数量\t介绍', 'id,name,count,info,nbt')

    @items.get(False, '请输入要使用的物品编号')
    def _(id, _):
        exec(items[id].nbt, {'session': session, 'user': user})
        assert user.remove(id, 1)
        return '使用成功！'

    await items.send_result()
