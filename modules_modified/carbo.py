import json
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Image, Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from aworda.lbot.function import LBotFunctionRegister

import aiofiles
import ujson
import random

channel = Channel.current()


@channel.use(
    ListenerSchema(
        [GroupMessage],
        inline_dispatchers=[LBotFunctionRegister("carbo")],
        decorators=[MatchContent("猫猫虫")],
    )
)
async def facepp(app: Ariadne, group: Group, source: Source):
    async with aiofiles.open("./resource/carbo.json") as f:
        data = ujson.loads(await f.read())
        url = random.choice(data["urls"])
        await app.send_group_message(
            group,
            MessageChain(
                "你要的猫猫虫图来啦!",
                Image(url=url),
            ),
            quote=source,
        )
