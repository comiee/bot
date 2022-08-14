from nonebot import on_command, CommandSession, MessageSegment
import qrcode
#from pyzbar import pyzbar
from PIL import Image
import aiohttp
from io import BytesIO
import os


@on_command('二维码')
async def _(session: CommandSession):
    for i in session.ctx['message']:
        if i['type'] == 'image':  # 识别二维码
            await session.send('暂不支持识别二维码')
            return
            url = i['data']['url']
            async with aiohttp.ClientSession() as clientSession:
                async with clientSession.get(url) as resp:
                    img = Image.open(BytesIO(await resp.read()))
            if res := pyzbar.decode(img):
                for j in res:
                    text = j.data.decode()
                    await session.send(text)
            else:
                await session.send('二维码识别失败！')
            break  # 找到图片则跳出
    else:  # 生成二维码
        if text := session.current_arg_text:
            img = qrcode.make(data=text)
            img.save('temp.jpg')
            await session.send(MessageSegment.image(os.getcwd() + r'\temp.jpg'))
            os.remove('temp.jpg')
        else:#没有参数，等待下条消息
            session.get('img', prompt='未找到图片或文字，请继续输入')
