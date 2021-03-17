"""用于数据库操作"""

import pymysql

db = pymysql.connect(
    host='localhost',
    user='comiee',
    password='19980722',
    database='mei',
    autocommit=True,
)
cur = db.cursor()


def get_user(session):
    """获取用户qq"""
    try:
        return int(session)
    except TypeError:
        return session.ctx['user_id']


def is_columns(table_name, column_name):
    """判断column_name是不是table_name中的一列"""
    return cur.execute(f'''
        select * from information_schema.columns where table_name={table_name!r} and column_name={column_name!r};
    ''')


def is_ban(session):
    """判断该用户是否在黑名单中"""
    user = get_user(session)
    return cur.execute(f'select * from ban where qq={user}')
