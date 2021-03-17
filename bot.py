import nonebot
import config
from os import path

nonebot.init(config)
nonebot.load_plugins(
    path.join(path.dirname(__file__), 'plugins'),
    'plugins'
)

nonebot.run()
