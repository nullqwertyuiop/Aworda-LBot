from datetime import datetime
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Quote, Source
from graia.ariadne.message.parser.base import ContainKeyword, DetectPrefix
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent
from graia.ariadne.model import Friend, Group, Member
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.broadcast.builtin.event import ExceptionThrowed
from model import GroupHistoryMessage, PrivateHistoryMessage
from loguru import logger
from utils.text2image import create_image
from io import StringIO
import traceback


channel = Channel.current()


@channel.use(
    ListenerSchema(
        [GroupMessage],
    )
)
async def group_message_listener(
    msg: MessageChain, group: Group, member: Member, db: GroupHistoryMessage
):
    await GroupHistoryMessage(
        group=group.id,
        sender=member.id,
        message=msg.asPersistentString(),
        time=datetime.now(),
    ).insert()
    logger.success("[DataBase] Message have been saved")


@channel.use(
    ListenerSchema(
        [FriendMessage],
    )
)
async def friend_message_listener(
    msg: MessageChain, friend: Friend, db: PrivateHistoryMessage
):
    await PrivateHistoryMessage(
        sender=friend.id, message=msg.asPersistentString(), time=datetime.now()
    ).insert()
    logger.success("[DataBase] Message have been saved")


@channel.use(
    ListenerSchema(
        [BotInvitedJoinGroupRequestEvent],
    )
)
async def bot_invited_join_group_request_listener(
    event: BotInvitedJoinGroupRequestEvent,
):
    await event.accept()


async def make_msg_for_unknow_exception(event):
    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()
    msg = str(
        f"异常事件：\n{str(event.event)}"
        + f"\n异常类型：\n{type(event.exception)}"
        + f"\n异常内容：\n{str(event.exception)}"
        + f"\n异常追踪：\n{tb}"
    )
    image = await create_image(msg)
    return MessageChain.create([Plain("发生未捕获的异常\n"), Image(data_bytes=image)])


@channel.use(ListenerSchema([ExceptionThrowed]))
async def except_handle(app: Ariadne, event: ExceptionThrowed):
    if isinstance(event.exception, IndexError):
        return
    if isinstance(event.event, MessageEvent):
        source = event.event.messageChain.getFirst(Source)
        await app.sendMessage(
            event.event, await make_msg_for_unknow_exception(event), quote=source
        )
