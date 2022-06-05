from graia.ariadne import Ariadne
from graia.ariadne.message.element import Quote
from graia.ariadne.message.parser.base import ContainKeyword, DetectPrefix
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from aworda.lbot.permission import MasterPermission
from aworda.lbot.function import LBotFunctionRegister

import asyncio

channel = Channel.current()


@channel.use(
    ListenerSchema(
        [GroupMessage, FriendMessage],
        inline_dispatchers=[
            LBotFunctionRegister("bot_manage", MasterPermission(), "干啥呢，坏蛋")
        ],
        decorators=[DetectPrefix("#broadcast")],
    )
)
async def broadcast(app: Ariadne, event: MessageEvent, chain: MessageChain):
    msg = chain.asSendable().removeprefix("#broadcast ")
    groups = await app.getGroupList()
    groups_count = len(groups)
    sleep_time = 1
    total_sleep_time = groups_count * sleep_time
    await app.sendMessage(
        event,
        MessageChain.create(
            f"开始广播，共{groups_count}个群，每个群每{sleep_time}秒广播一次，总共需要{total_sleep_time}秒"
        ),
    )
    for group in groups:
        await app.sendGroupMessage(group, msg)
        await asyncio.sleep(sleep_time)
    await app.sendMessage(event, MessageChain.create(f"广播完成"))
