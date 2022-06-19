import abc
from types import TracebackType
from typing import Union
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.ariadne.event.message import MessageEvent
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne import get_running
from . import LBot
from typing import Optional


class BasePermission:

    denied_message: Optional[Union[str, MessageChain]] = None

    def __init__(self, denied_message: Optional[Union[str, MessageChain]] = None):
        self.denied_message = denied_message

    @abc.abstractmethod
    async def target(self, event: BaseEvent) -> bool:
        raise NotImplementedError()


class PermissionStatus:
    def __init__(self, status: bool):
        self.status = status


class PersonPermission(BasePermission):
    def __init__(
        self, sender: int, denied_message: Optional[Union[str, MessageChain]] = None
    ):
        self.denied_message = denied_message
        self.sender = sender

    async def target(self, event: MessageEvent) -> bool:
        return event.sender.id == self.sender


class MasterPermission(PersonPermission):
    def __init__(self, denied_message: Optional[Union[str, MessageChain]] = None):
        lbot = LBot.get_running()
        self.denied_message = denied_message
        self.sender = lbot.config.bot.master


class Stop(BasePermission):
    async def target(self, event: BaseEvent) -> bool:
        return False


class AllAllow(BasePermission):
    def __init__(self):
        pass

    async def target(self, event: BaseEvent) -> bool:
        return True


class PermissionDispatcher(BaseDispatcher):
    def __init__(
        self,
        permission: BasePermission,
    ):
        """
        :param permission: 权限
        """
        self.permission = permission

    async def afterDispatch(
        self,
        interface: DispatcherInterface,
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        denied_message = self.permission.denied_message
        if await self.permission.target(interface.event):
            return interface
        else:
            if denied_message:
                if not isinstance(denied_message, MessageChain):
                    denied_message = MessageChain.create(denied_message)
                app = get_running()
                await app.sendMessage(interface.event, denied_message)
            raise ExecutionStop()

    async def catch(self, interface: DispatcherInterface):
        return await super().catch(interface)
