from graia.ariadne import Ariadne
from graia.ariadne.message.element import Image, Quote, Source
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.model import Group
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from aworda.lbot.function import LBotFunctionRegister
from config import get_config

import aiohttp
import base64

channel = Channel.current()


async def face_join_face(img1: str, img2: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api-cn.faceplusplus.com/imagepp/v1/mergeface",
            data={
                "api_key": get_config().facepp.api_key,
                "api_secret": get_config().facepp.api_secret,
                "template_url": img1,
                "merge_url": img2,
            },
        ) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                result_bytes = base64.b64decode(resp_json["result"])
                return MessageChain.create("转基因成功()", Image(data_bytes=result_bytes))
            else:
                resp_json = await resp.json()
                return MessageChain.create(
                    f"转基因失败惹()\n好像是因为{resp_json['error_message']}"
                )


@channel.use(
    ListenerSchema(
        [GroupMessage],
        inline_dispatchers=[LBotFunctionRegister("face_join_face")],
        decorators=[DetectPrefix("#合成")],
    )
)
async def facepp(app: Ariadne, group: Group, chain: MessageChain, source: Source):
    if not len(chain.get(Image)) == 2:
        await app.sendGroupMessage(
            group, MessageChain.create("噫，你倒是发两张图片啊"), quote=source
        )
        return
    img1: str = chain.get(Image)[0].url
    img2: str = chain.get(Image)[1].url
    await app.sendGroupMessage(
        group,
        await face_join_face(img1, img2),
        quote=source,
    )
