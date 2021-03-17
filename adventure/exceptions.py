class Finish(Exception):
    """一个Scene完成"""
    pass


class Exit(Exception):
    """退出整个游戏"""


class Dead(Exception):
    """Entity死亡"""

    def __init__(self, entity):
        self.entity = entity
