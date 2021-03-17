from nonebot import on_command, CommandSession
from PIL import Image
from io import BytesIO
import requests

ASCII_CHAR = r'''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. '''


def get_char(r, g, b, alpha=256):  # alpha透明度
    if alpha == 0:
        return ' '
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)  # 计算灰度
    unit = (256.0 + 1) / len(ASCII_CHAR)
    return ASCII_CHAR[int(gray / unit)]  # 不同的灰度对应着不同的字符


def produce(img, size):
    w, h = size, int(img.size[1] / img.size[0] * size / 2)
    img = img.resize((w, h))
    res = ''
    for j in range(h):
        for i in range(w):
            res += get_char(*img.getpixel((i, j)))
        res += '\n'
    return res


@on_command('字符画')
async def _(session: CommandSession):
    if session.current_arg_text:
        session.state['size'] = int(session.current_arg_text)
    for i in session.ctx['message']:
        if i['type'] == 'image':
            session.state['url'] = i['data']['url']
            break
    else:
        session.pause('未发现图片，等待输入中')

    url = session.state['url']
    size = session.state.get('size', 100)
    img = Image.open(BytesIO(requests.get(url).content))
    await session.send(produce(img, size))
