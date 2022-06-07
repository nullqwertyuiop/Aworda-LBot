from datetime import datetime
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Quote
from graia.ariadne.message.parser.base import ContainKeyword, DetectPrefix
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent
from graia.ariadne.model import Friend, Group, Member
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from model import GroupHistoryMessage, PrivateHistoryMessage
from loguru import logger

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
