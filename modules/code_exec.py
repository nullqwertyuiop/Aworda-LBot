# coding: utf-8
import traceback
import subprocess
import asyncio
from typing import Union
from arclet.alconna import Args, AllParam, Option
from arclet.alconna.graia import Alconna, AlconnaDispatcher
from arclet.alconna.graia.dispatcher import AlconnaProperty
from arclet.alconna.graia.saya import AlconnaSchema
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema
from graia.ariadne.message.element import Image
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.model import Group, Friend
from graia.ariadne.app import Ariadne

from aworda.lbot.permission import MasterPermission
from aworda.lbot.function import LBotFunctionRegister
from aworda.lbot import LBot
from utils.text2image import create_image

saya = Saya.current()
channel = Channel.current()

code = Alconna(
    "执行",
    Args["code;S":str],
    headers=["#"],
    options=[Option("out", Args["name;O":str:"res"])],
    help_text=f"执行简易代码 Example: #执行 print(1+1);",
)

shell = Alconna(
    "shell",
    Args["code":AllParam],
    headers=["#"],
    help_text=f"执行命令行语句 Example: #shell echo hello;",
    is_fuzzy_match=True,
)


@channel.use(AlconnaSchema(AlconnaDispatcher(alconna=code, help_flag="reply")))
@channel.use(
    ListenerSchema(
        [GroupMessage, FriendMessage], inline_dispatchers=[LBotFunctionRegister("code_exec",MasterPermission(),"啊嘞，好像权限不够嘞")]
    )
)
async def _(
    app: Ariadne,
    sender: Union[Group, Friend],
    message: MessageChain,
    result: AlconnaProperty,
):
    arp = result.result
    codes = message.asDisplay().split("\n")
    output = arp.query("out.name", "res")
    if len(codes) == 1:
        return
    for _code in codes[1:]:
        if "exit(" in _code or "os." in _code or "system(" in _code:
            return await app.sendMessage(
                sender, MessageChain.create("Execution terminated")
            )
    lcs = {}
    try:
        exec(
            "async def rc():\n    "
            + "    ".join([_code + "\n" for _code in codes[1:]])
            + "    await asyncio.sleep(0.1)\n"
            + "    return locals()",
            {**globals(), **locals()},
            lcs,
        )
        print(lcs["rc"])
        data = await lcs["rc"]()
        code_res = data.get(output)
        if code_res is not None:
            return await app.sendMessage(
                sender, MessageChain.create(f"{output}: {code_res}")
            )
        else:
            return await app.sendMessage(sender, MessageChain.create("execute success"))
    except Exception as e:
        return await app.sendMessage(
            sender,
            MessageChain.create(
                "\n".join(
                    traceback.format_exception(e.__class__, e, e.__traceback__, limit=1)
                )
            ),
        )


@channel.use(AlconnaSchema(AlconnaDispatcher(alconna=shell, help_flag="reply")))
@channel.use(
    ListenerSchema(
        [GroupMessage, FriendMessage],
        inline_dispatchers=[LBotFunctionRegister("shell_exec",MasterPermission(),"再这样下去，霖念会生气的💧💧")],
    )
)
async def _(app: Ariadne, sender: Union[Group, Friend], result: AlconnaProperty):
    try:
        res = subprocess.run(
            result.result.main_args["code"][0],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode("utf-8")
    except UnicodeDecodeError:
        res = subprocess.run(
            result.result.main_args["code"][0],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode("gbk")
    await asyncio.sleep(0)
    return await app.sendMessage(
        sender,
        MessageChain.create(Image(data_bytes=(await create_image(res, cut=120)))),
    )
