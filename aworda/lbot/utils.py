from typing import List, Optional
from graia.broadcast import Broadcast
from graia.broadcast.entities.dispatcher import BaseDispatcher
from aworda.lbot.dispatcher import ContextDispatcher, DocumentDispatcher


def global_dispatcher(
    broadcast: Broadcast, dispatchers: Optional[List[BaseDispatcher]] = None
):
    """
    全局广播器
    """
    if dispatchers:
        for dispatcher in dispatchers:
            broadcast.finale_dispatchers.append(dispatcher)
    broadcast.finale_dispatchers.append(ContextDispatcher())
    broadcast.finale_dispatchers.append(DocumentDispatcher())
