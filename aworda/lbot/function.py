from typing import Dict, List, Optional, Union
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.typing import P
from graia.broadcast.entities.dispatcher import BaseDispatcher
import contextvars
from .permission import AllAllow, BasePermission, PermissionDispatcher, Stop

functions = contextvars.ContextVar("aworda_lbot_functions")
functions.set({})


class LBotFunctionRegister(PermissionDispatcher):
    def __init__(
        self,
        name: str,
        defualt_permission: BasePermission = AllAllow(),
        denied_message: Optional[Union[str, MessageChain]] = None,
    ):
        self.name = name
        self.permission = defualt_permission
        self.denied_message = denied_message
        funcs = functions.get()
        funcs[name] = self
        functions.set(funcs)


class LBotFunctionManager:
    def __init__(self, name: str):
        self.function: LBotFunctionRegister = functions.get()[name]

    def save(self):
        funcs = functions.get()
        funcs[self.function.name] = self.function
        functions.set(funcs)

    def change_permission(self, permission: BasePermission):
        self.function.permission = permission
        self.save()

    def stop_function(self):
        self.function.permission = Stop()
        self.save()

    @staticmethod
    def get_all_functions() -> Dict[str, LBotFunctionRegister]:
        return functions.get()
