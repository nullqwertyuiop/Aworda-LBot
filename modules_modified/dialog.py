from time import sleep
from graia.ariadne.model.relationship import MemberPerm
from loguru import logger
from typing import Dict
from graia.ariadne import Ariadne
from graia.ariadne.message.element import At, Plain, Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.saya.channel import Channel
from beanie import Document
from config import get_config
from aworda.lbot import LBot
from graia.saya.builtins.broadcast.schema import ListenerSchema
from aworda.lbot.function import LBotFunctionRegister


import aiohttp
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
async def doctor(app: Ariadne, group: Group, source: Source, msg: MessageChain):
    stringed_message = msg.display
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
            await app.send_group_message(
                group, MessageChain([Plain(result)]), quote=source
            )
            break


multi_language = [
    "Nullとセックスしたい",
    "I want to have sex with Null",
    "我他妈好想和null做爱",
    "я действительно хочу трахаться с нулем",
    "난 정말 null 섹스하고 싶어",
    "je veux vraiment baiser null",
]


@channel.use(ListenerSchema([GroupMessage], decorators=[MatchContent("fucknull")]))
async def fuck_null(app: Ariadne, group: Group):
    await app.send_group_message(
        group, MessageChain(At(1417324298), Plain(random.choice(multi_language)))
    )


async def get_reply(text: str, group: int):
    async with aiohttp.ClientSession() as s:
        async with s.get(
            get_config().ai, params={"text": text, "session": str(group)}
        ) as r:
            return (await r.json())["result"]


class LuckyNumber(Document):
    group: int
    lucky: int
    max_value: int


def dice(ln: LuckyNumber):
    if ln.lucky == random.randint(1, ln.max_value):
        return True
    return False


@channel.use(
    ListenerSchema(
        [GroupMessage],
        inline_dispatchers=[LBotFunctionRegister("chatterbot")],
    )
)
async def touchfish(
    app: Ariadne,
    group: Group,
    msg: MessageChain,
    source: Source,
    member: Member,
    unsure: LuckyNumber,
):
    if msg.display.startswith("#调整概率") and (
        member.permission > MemberPerm.Member
        or member.id == LBot.get_running().config.bot.master
    ):
        random_max = int(msg.removeprefix("#调整概率").display)
        lucky = await LuckyNumber.find(LuckyNumber.group == group.id).to_list()
        if len(lucky) == 0:
            if (
                len(await LuckyNumber.find(LuckyNumber.group == group.id).to_list())
                == 0
            ):
                await LuckyNumber(
                    group=group.id, lucky=random.randint(1, 100), max_value=100
                ).insert()
        else:
            lucky = lucky[0]
            await lucky.set(
                {"lucky": random.randint(1, random_max), "max_value": random_max}
            )

        await app.send_group_message(
            group, MessageChain(f"现在ai回复的概率是 {1 / random_max * 100} ％")
        )
        return

    if msg.has(At):

        if msg.get_first(At).target == app.account:
            text = msg.get_first(Plain).text
            await app.send_group_message(
                group, MessageChain(await get_reply(text, group.id)), quote=source
            )
    if msg.has(Plain):
        if not len(msg) == 2:
            return
        if len(await LuckyNumber.find(LuckyNumber.group == group.id).to_list()) == 0:
            await LuckyNumber(
                group=group.id, lucky=random.randint(1, 100), max_value=100
            ).insert()
        lucky = (await LuckyNumber.find(LuckyNumber.group == group.id).to_list())[0]
        if dice(lucky):
            text = msg.display
            await app.send_group_message(
                group, MessageChain(await get_reply(text, group.id)), quote=source
            )
