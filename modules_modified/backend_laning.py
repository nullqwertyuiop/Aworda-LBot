from datetime import datetime
from graia.ariadne.app import Ariadne
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import MatchResult, Twilight
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Source, At
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel, Saya
from loguru import logger
import time

channel = Channel.current()
saya = Saya.current()


@channel.use(ConsoleSchema([Twilight.from_command("laning {id} {message}")]))
async def console_chat(app: Ariadne, id: MatchResult, message: MatchResult):
    group_id = id.result.display
    await app.send_group_message(int(group_id), message.result)


@channel.use(ConsoleSchema([Twilight.from_command("exit")]))
async def console_exit(app: Ariadne):
    app.stop()


@channel.use(ConsoleSchema([Twilight.from_command("伪造群消息 {group} {sender} {msg}")]))
async def console_fake_event(
    app: Ariadne, group: MatchResult, sender: MatchResult, msg: MatchResult
):
    member = await app.get_member(int(group.result.display), int(sender.result.display))
    app.broadcast.postEvent(
        GroupMessage(
            messageChain=MessageChain(At(app.account), msg.result.display),
            sender=member,
        )
    )


@channel.use(ConsoleSchema([Twilight.from_command("saya {function} {module}")]))
async def console_saya(app: Ariadne, function: MatchResult, module: MatchResult):
    if function.result.display == "install":
        with saya.module_context():
            saya.require(module.result.display)
        logger.info(f"{module.result.display} installed")
    elif function.result.display == "uninstall":
        saya.uninstall_channel(saya.channels.get(module.result.display))
        logger.info(f"{module.result.display} uninstalled")
    elif function.result.display == "reload":
        channel = saya.channels.get(module.result.display)
        saya.uninstall_channel(channel)
        time.sleep(1)
        try:
            with saya.module_context():
                saya.require(module.result.display)
        except:
            logger.error(f"{module.result.display} reload failed")
    elif function.result.display == "list":
        logger.info(saya.channels)
