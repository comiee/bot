from tools.sql import cur
from tools.state import InSession
from tools.functions import to_int
from collections import namedtuple
import re


class ItemList(InSession):
    """物品列表
    参数：
    session：当前的session
    data：sql语句或二维元组：如果是sql语句会先执行此语句，然后将得到的结果作为data；
        元组内为需要放入列表中的数据，会以【每行第一项：该行的namedtuple】的形式放在self.items中，供__getitem__调用
    title：字符串：显示时的标题
    columns：字符串列表或换行符和逗号分割的数组：显示时的列名
    keys：字符串列表或逗号分割的字符串：提供给data使用的namedtuple的元素名
    n：整数：每页显示的行数
    """

    def __init__(self, session, data, title, columns, keys, n=10):
        super().__init__(session)
        if isinstance(keys, str):
            keys = keys.split(',')
        if isinstance(columns, str):
            columns = re.split(r'[\t,]', columns)
        if isinstance(data, str):
            cur.execute(data)
            data = cur.fetchall()

        self.title = title
        self.columns = columns
        nt = namedtuple('nt', keys)
        self.items = {i[0]: nt(*i) for i in data}
        lines = ['\t'.join(map(str, i[:len(columns)])) for i in self.items.values()]
        self.pages = [lines[i:i + n] for i in range(0, len(lines), n)] or ['']
        self.p = 1
        self.result = []

    def __str__(self):
        """显示当前页"""
        return f'{self.title}【第{self.p}/{len(self.pages)}页】：\n' + \
               "\t".join(self.columns) + '\n' + \
               '\n'.join(self.pages[self.p - 1])

    def __getitem__(self, key):
        """获取内部数据"""
        return self.items[key]

    def analyse(self, prompt):
        """向用户询问prompt，判断回答是否是翻页，是则执行翻页，不是则返回回答"""
        while args := self.session.get('args', prompt=f'{self}\n{prompt}'):
            if match := re.search(r'([上下])[一1]?页', args):
                p = self.p + {'上': -1, '下': 1}[match.group(1)]
            elif match := re.search(r'第?([\d一二三四五六七八九十零]+)页', args):
                p = to_int(match.group(1))
            else:
                return args
            if 0 < p <= len(self.pages):
                self.p = p
            del self.session.state['args']

    def get(self, repeatable, ask):
        """显示并根据用户的输入翻页或执行函数

        :param repeatable: 能否批量购买多个
        :param ask: 询问的语句，会在物品列表和tips之间显示
        """
        if repeatable:
            pattern = r'\d+\s+\d+|\d+'
        else:
            pattern = r'\d+'
        tips = '使用 第x页、上一页、下一页 翻页。' + [
            '批量操作请用非数字字符隔开',
            '物品与数量用空白字符隔开，物品与物品用非空白字符隔开。不输入数量默认一个'
        ][repeatable]

        def get_func(func):
            """func：接收id和count，返回result"""
            if args := self.analyse(f'{ask}：\n（{tips}）'):
                for arg in re.findall(pattern, args):
                    try:
                        id, count, *_ = *map(int, arg.split()), 1
                        assert id in self.items
                    except:
                        self.result.append('错误输入，命令已取消')
                    else:
                        self.result.append(func(id, count))

        return get_func

    async def send_result(self):
        """发送执行的结果"""
        if len(self.result) == 0:
            await self.session.send('错误输入，命令已取消。')
        elif len(self.result) == 1:
            await self.session.send(self.result[0])
        else:
            await self.session.send('执行结果：\n' + '\n'.join(f'第{i + 1}条：{s}' for i, s in enumerate(self.result)))

    async def show(self):
        """显示。如果有多页提供翻页功能"""
        if len(self.pages) == 1:
            await self.session.send(str(self))
            return

        if self.analyse(f'使用 第x页、上一页、下一页 翻页。'):
            await self.session.send('已退出。')
