import os
from pathlib import Path
from time import sleep
from loguru import logger
from creart import create
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.ariadne.console import Console  # 不是 from rich.console import Console 噢
from graia.ariadne.console.saya import ConsoleBehaviour
from arclet.alconna.graia.saya import AlconnaBehaviour
from arclet.alconna.manager import command_manager
from aworda.lbot import LBot
from aworda.lbot.utils import global_dispatcher
from config import init_configs


broadcast = create(Broadcast)
con = Console(broadcast=broadcast, prompt="小霖念> ")
saya = Saya(broadcast)
saya.install_behaviours(BroadcastBehaviour(broadcast))
saya.install_behaviours(ConsoleBehaviour(con))
saya.install_behaviours(AlconnaBehaviour(broadcast, command_manager))
global_dispatcher(broadcast)
init_configs("./config/api_keys.json")

lbot = LBot(broadcast=broadcast)

with saya.module_context():
    for i in os.listdir("./modules_modified"):
        try:
            if i.startswith("_stop"):
                logger.info(f"忽略模块 {i}")
                continue
            if i.endswith(".py"):
                saya.require(f"modules_modified.{i[:-3]}")
                logger.info(f"Loaded module {i[:-3]}")
            elif Path(f"./modules_modified/{i}").is_dir():
                saya.require(f"modules_modified.{i}")
                logger.info(f"Loaded module {i}")
            sleep(0.3)
        except Exception as e:
            logger.exception(e)


lbot.launch_blocking()
