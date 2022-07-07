import json
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Image, Plain, Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from pydantic.types import conint
from aworda.lbot.function import LBotFunctionRegister

import aiofiles
import ujson
import random
import jieba

channel = Channel.current()

ILLNESS = ["疼", "痛"]


@channel.use(
    ListenerSchema(
        [GroupMessage],
        inline_dispatchers=[LBotFunctionRegister("key_reply")],
    )
)
async def facepp(app: Ariadne, group: Group, source: Source, msg: MessageChain):
    stringed_message = msg.asDisplay()
    for i in ILLNESS:
        if i in stringed_message:

            jieba.load_userdict("./resource/illness.txt")
            words = jieba.lcut(stringed_message)
            index = 0
            for w in words:
                if w in ILLNESS:
                    break
                index += 1
            result = words[index - 1] + "癌"
            await app.sendGroupMessage(
                group, MessageChain.create([Plain(result)]), quote=source
            )
            break
