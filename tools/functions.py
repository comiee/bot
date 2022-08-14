from typing import Union
from datetime import datetime, timedelta
import re


class Num:
    """
    to_int函数中使用
    n：数值
    u：单位
    """

    def __init__(self, n, u):
        self.n = n
        self.u = u

    def __int__(self):
        return self.n * self.u


def to_int(s: Union[int, str]):
    """汉字转为数字"""
    if isinstance(s, int):
        return s
    if re.search(r'\d', s):
        return int(re.sub(r'[^\d]', '', s))
    if s and s[0] in '-负':
        return -to_int(s[1:])
    nums = {**dict(zip('〇一二三四五六七八九', range(10))),
            **dict(zip('零壹贰叁肆伍陆柒捌玖', range(10))),
            **dict(zip(map(str, range(10)), range(10))),
            '两': 2, '貮': 2}
    units = {**dict(zip('十百千万', map((10).__pow__, range(1, 5)))),
             **dict(zip('拾佰仟', map((10).__pow__, range(1, 4)))),
             '亿': 10 ** 8, '億': 10 ** 8, '兆': 10 ** 12}
    stack = []
    for c in s:
        if c in nums:
            if stack and stack[-1].u == 1 and stack[-1].n != 0:
                stack[-1].n = stack[-1].n * 10 + nums[c]
            else:
                stack.append(Num(nums[c], 1))
        elif c in units:
            if not stack:
                stack.append(Num(1, 1))
            if units[c] < stack[-1].u:
                stack.append(Num(1, units[c]))
            else:
                temp = 0
                while stack and stack[-1].u <= units[c]:
                    temp += int(stack.pop())
                stack.append(Num(temp, units[c]))
    if len(stack) >= 2 and stack[-1].u == 1 and stack[-1].n < 10 and stack[-2].u > 1:
        stack[-1].u = stack[-2].u // 10
    return sum(map(int, stack))


def to_num(n):
    """数字转为汉字"""
    n = int(n)
    if n == 0:
        return '零'
    units = {10 ** 8: '亿', 10 ** 4: '万'}
    for u in units:
        if n > u:
            return to_num(n // u) + units[u] + '零' * (n % u < u // 10) + to_num(n % u)
    units = {1000: '千', 100: '百', 10: '十'}
    nums = '零一二三四五六七八九'
    res = ''
    for u in units:
        if n >= u:
            if n // u == 1 and u == 10 and not res:
                res += '十'
            else:
                res += nums[n // u] + units[u]
        elif n and res and res[-1] != '零':
            res += '零'
        n %= u
    if n:
        res += nums[n]
    return res


def analyse_time(s):
    res = now = datetime.now()
    res = res.replace(microsecond=0)
    if m := re.match(r'.*(下?)(?:星期|周)(.)(下午)?(?:(.*?)[点时](半)?)?(?:(.*?)分钟?)?(?:(.*?)秒钟?)?', s):
        next_week, weekday, afternoon, hour, half, minute, second = m.groups()
        if half:
            minute = 30
        if afternoon:
            hour += 12
        res = res - timedelta(res.isoweekday()) + timedelta(to_int(weekday) or 7)
        if res < now or next_week:
            res += timedelta(7)
    elif m := re.match(r'(?:(.*?)年)?(?:(.*?)月)?(?:(.*?)[日天号])?(下午)?'
                       r'(?:(.*?)个?(半)?小?[点时])?(?:(.*?)分钟?)?(?:(.*?)秒钟?)?[之以]?后', s):
        if not any(m.groups()):
            return None
        year, month, day, afternoon, hour, half, minute, second = m.groups()
        if year:
            res = res.replace(year=res.year + to_int(year))
        if month:
            month = to_int(month)
            res = res.replace(year=res.year + month // 12)
            res = res.replace(month=res.month + month % 12)
        if hour == '半':
            hour = 0
            minute = 30
        if afternoon:
            hour = to_int(hour) + 12
        if half:
            minute = 30
        for x in ['day', 'hour', 'minute', 'second']:
            if eval(x):
                res += timedelta(**{x + 's': to_int(eval(x))})
        return res
    else:
        m = re.match(r'(?:(.*?)年)?(?:(.*?)月)?(?:(.*?)[日天号])?(下午)?'
                     r'(?:(.*?)[点时](半)?)?(?:(.*?)分钟?)?(?:(.*?)秒钟?)?', s)
        if not any(m.groups()):
            return None
        year, month, day, afternoon, hour, half, minute, second = m.groups()
        d = {'今': 0, '明': 1, '后': 2, '大后': 3}
        if year in d:
            year = now.year + d[year]
        elif year and len(year) == 2:
            year = '20' + year
        if month and month == '下个':
            month = now.month + 1
        if day in d:
            day = now.day + d[day]
        if year:  res = res.replace(year=to_int(year))
        if month: res = res.replace(month=to_int(month))
        if day:   res = res.replace(day=to_int(day))
        if afternoon:
            hour = to_int(hour) + 12
        if half:
            minute = 30
    res = res.replace(hour=to_int(hour) if hour else 12,
                      minute=to_int(minute) if minute else 0,
                      second=to_int(second) if second else 0)
    return res
