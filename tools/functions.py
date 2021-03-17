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


def to_int(s):
    """汉字转为数字"""
    if isinstance(s, int) or s.isdigit():
        return int(s)
    nums = {**dict(zip('〇一二三四五六七八九', range(10))),
            **dict(zip('零壹贰叁肆伍陆柒捌玖', range(10))),
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
