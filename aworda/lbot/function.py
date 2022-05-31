from types import TracebackType
from typing import List, Optional, Union
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.ariadne.message.element import Quote
from graia.ariadne.message.chain import MessageChain
from beanie import Document
from . import LBot


class FunctionControl(Document):
    function_name: str
    blocked_people: List[int]
    blocked_groups: List[int]


# class FunctionController(BaseDispatcher):
