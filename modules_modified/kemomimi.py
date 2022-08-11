from graia.ariadne import Ariadne
from graia.ariadne.message.element import Image, Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from aworda.lbot.function import LBotFunctionRegister

import aiohttp
import random

channel = Channel.current()


@channel.use(
    ListenerSchema(
        [GroupMessage],
        inline_dispatchers=[LBotFunctionRegister("kemomimi")],
        decorators=[MatchContent("#kk")],
    )
)
async def facepp(app: Ariadne, group: Group, source: Source):
    async with aiohttp.ClientSession() as session:
        await app.send_group_message(
            group,
            MessageChain(
                "你要的 kemomimi 图来啦!",
                Image(
                    url=f"https://brx86.gitee.io/kemomimi/{random.randint(0,581)}.jpg"
                ),
            ),
            quote=source,
        )
