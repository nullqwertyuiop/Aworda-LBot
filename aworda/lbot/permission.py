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
    @abc.abstractmethod
    async def target(self, event: BaseEvent) -> bool:
        raise NotImplementedError()


class PermissionStatus:
    def __init__(self, status: bool):
        self.status = status


class PersonPermission(BasePermission):
    def __init__(self, sender: int):
        self.sender = sender

    async def target(self, event: MessageEvent) -> bool:
        return event.sender.id == self.sender


class MasterPermission(PersonPermission):
    def __init__(self):
        lbot = LBot.get_running()
        self.sender = lbot.config.bot.master


class Stop(BasePermission):
    async def target(self, event: BaseEvent) -> bool:
        return False



class AllAllow(BasePermission):
    async def target(self, event: BaseEvent) -> bool:
        return True


class PermissionDispatcher(BaseDispatcher):
    def __init__(
        self,
        permission: BasePermission,
        denied_message: Optional[Union[str, MessageChain]] = None,
    ):
        """
        :param permission: 权限
        :param denied_message: 拒绝消息 可以是字符串或者 MessageChain 可以不填入此时权限不足将会沉默 推荐在没有使用任何其他消息链处理器的情况下使用 alconna dispatcher 请启用 不继续执行模式
        :param stop_message: 遇到 Stop Permission 将会抛出 ExecutionStop 异常 可以是字符串或者 MessageChain 可以不填入此时权限不足将会沉默 推荐在没有使用任何其他消息链处理器的情况下使用 alconna dispatcher 请启用 不继续执行模式
        """
        self.permission = permission
        self.denied_message = denied_message

    async def afterDispatch(
        self,
        interface: DispatcherInterface,
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        if await self.permission.target(interface.event):
            return interface
        else:
            if self.denied_message:
                if not isinstance(self.denied_message, MessageChain):
                    self.denied_message = MessageChain.create(self.denied_message)
                app = get_running()
                await app.sendMessage(interface.event, self.denied_message)
            raise ExecutionStop()

    async def catch(self, interface: DispatcherInterface):
        return await super().catch(interface)
