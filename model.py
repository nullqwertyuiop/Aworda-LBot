from beanie import Document
from datetime import datetime
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from typing import Optional


class SignInInfo(Document):
    user: int
    days: int
    favorability: int
    last_time: datetime


class GroupHistoryMessage(Document):

    sender: int
    group: int
    message: str
    time: datetime
    messageChain: Optional[MessageChain] = None


class PrivateHistoryMessage(Document):

    sender: int
    message: str
    time: datetime
    messageChain: Optional[MessageChain] = None
