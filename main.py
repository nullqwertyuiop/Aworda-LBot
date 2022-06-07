import os
from pathlib import Path
from loguru import logger
from graia import saya
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from arclet.alconna.graia.saya import AlconnaBehaviour
from arclet.alconna.manager import command_manager
from aworda.lbot import LBot
from aworda.lbot.utils import global_dispatcher
from config import init_configs


broadcast = Broadcast()
saya = Saya(broadcast)
saya.install_behaviours(BroadcastBehaviour(broadcast))
saya.install_behaviours(AlconnaBehaviour(broadcast, command_manager))
global_dispatcher(broadcast)
init_configs("./config/api_keys.json")

lbot = LBot(broadcast=broadcast)

with saya.module_context():
    for i in os.listdir("./modules"):
        if i.startswith("_stop"):
            logger.info(f"忽略模块 {i}")
            continue
        if i.endswith(".py"):
            saya.require(f"modules.{i[:-3]}")
            logger.info(f"Loaded module {i[:-3]}")
        elif Path(f"./modules/{i}").is_dir():
            saya.require(f"modules.{i}")
            logger.info(f"Loaded module {i}")


lbot.launch_blocking()
