import asyncio
from pathlib import Path
import re
from graia.ariadne.event import message
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne

from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Face,
    Image as IMG,
    Plain as Text,
    Source,
)
from aworda.lbot.function import LBotFunctionRegister
from aworda.lbot.permission import Stop
from model import SignInInfo
import random

saya = Saya.current()
channel = Channel.current()
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import aiohttp
import os

try:
    import ujson as json
except ImportError:
    import json
RESOURCES_BASE_PATH = str(Path(rf"{os.getcwd()}/resource/sign-in"))

hitokoto_url = "https://v1.hitokoto.cn/"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("签到")],
        inline_dispatchers=[
            LBotFunctionRegister(
                "signin", defualt_permission=Stop(), denied_message="啊嘞，签到好像停用了捏"
            )
        ],
    )
)
async def sendmsg(
    app: Ariadne, msg: MessageChain, group: Group, member: Member, db: SignInInfo
):
    message_id = msg.getFirst(Source).id
    try:
        info = await SignInInfo.find(SignInInfo.user == member.id).to_list()
        info = info[0]
    except:
        info = []
    if not info:
        await SignInInfo(
            user=member.id,
            favorability=0,
            days=0,
            last_time=datetime.datetime(1990, 1, 1),
        ).insert()
    info = await SignInInfo.find(SignInInfo.user == member.id).to_list()
    info = info[0]
    if (
        info.last_time.day >= datetime.datetime.now().day
        and info.last_time.month == datetime.datetime.now().month
    ):
        await app.sendGroupMessage(
            group, MessageChain.create([Text("噫，你今天签了到了")]), quote=message_id
        )
        return
    avatar = await member.getAvatar()
    favorability = str(info.favorability + random.randint(10, 30))
    signin_frame = SignInFrameWork(
        member.id,
        member.name,
        favorability,
        info.days,
        await get_hitokoto(),
        avatar,
    )
    await info.set(
        {
            "days": info.days + 1,
            "favorability": favorability,
            "last_time": datetime.datetime.now(),
        }
    )

    def sign_in(signin_frame):
        result = (
            signin_frame.createAvatar()
            .createRoundImg()
            .createCanvas()
            .createAMagicCircle()
            .createTextBasemap()
            # Start processing
            .additionalMagicCircle()
            .additionalAvatar()
            .additionalTextBaseMap()
            # Must be the last step
            .additionalSignInInformation()
        )
        return result.get_bytes()

    await app.sendGroupMessage(
        group,
        MessageChain.create(
            [
                IMG(data_bytes=await asyncio.to_thread(sign_in, signin_frame)),
            ]
        ),
        quote=message_id,
    )


async def get_hitokoto() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(hitokoto_url) as resp:
            data = await resp.json()
            return data["hitokoto"]


class Tools:
    class Dict(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__

    @classmethod
    def dictToObj(cls, dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        d = cls.Dict()
        for k, v in dictObj.items():
            d[k] = cls.dictToObj(v)
        return d


class SignInFrameWork:

    FONT_ZHANKU = "zhanku.ttf"
    FONT_REEJI = "REEJI-HonghuangLiGB-SemiBold.ttf"

    def __init__(
        self,
        userQQ: int,
        nickname: str,
        favorability: str,
        days: int,
        hitokoto: str,
        avatar: bytes,
    ):
        self.userQQ = userQQ
        self.nickname = nickname
        self.favorability = favorability
        self.days = days
        self.hitokoto = hitokoto
        self._basemapSize = 640
        self.avatarSize = 256
        self._fontAttenuation = 2
        self._minimumFontLimit = 10
        self._magicCirclePlus = 30
        self._avatarVerticalOffset = 50
        self._textBaseMapSize = (540, 160)
        self._topPositionOfTextBaseMap = 425
        self._textBaseMapLeftPosition = int(
            (self._basemapSize - self._textBaseMapSize[0]) / 2
        )
        self._userInfo = "签 到 成 功"

        self._userInfoIntegration = f"签到天数  {self.days}   好感度  {self.favorability}"
        self._infoCoordinatesY = Tools.dictToObj(
            {
                "nickname": self._topPositionOfTextBaseMap + 26,
                "info": self._topPositionOfTextBaseMap + 64,
                "integration": self._topPositionOfTextBaseMap + 102,
                "hitokoto": self._topPositionOfTextBaseMap + 137,
            }
        )
        self._infoFontSize = Tools.dictToObj(
            {"nickname": 28, "info": 28, "integration": 25, "hitokoto": 25}
        )
        self._infoFontName = Tools.dictToObj(
            {
                "nickname": self.FONT_REEJI,
                "info": self.FONT_REEJI,
                "integration": self.FONT_REEJI,
                "hitokoto": self.FONT_ZHANKU,
            }
        )
        self.avatar = avatar

    @staticmethod
    def imageRadiusProcessing(img, centralA, radius=30):
        """处理图片四个圆角。
        :centralA: 中央区域的 A 通道值，当指定为 255 时全透，四角将使用 0 全不透
        """
        circle = Image.new("L", (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=centralA)
        w, h = img.size
        alpha = Image.new("L", img.size, centralA)
        upperLeft, lowerLeft = circle.crop((0, 0, radius, radius)), circle.crop(
            (0, radius, radius, radius * 2)
        )
        upperRight, lowerRight = (
            circle.crop((radius, 0, radius * 2, radius)),
            circle.crop((radius, radius, radius * 2, radius * 2)),
        )
        alpha.paste(upperLeft, (0, 0))
        alpha.paste(upperRight, (w - radius, 0))
        alpha.paste(lowerRight, (w - radius, h - radius))
        alpha.paste(lowerLeft, (0, h - radius))
        img.putalpha(alpha)
        return img

    @staticmethod
    def resize(img, size):
        return img.copy().resize(size, Image.ANTIALIAS)

    @staticmethod
    def gaussianBlur(img, radius=7):
        return img.copy().filter(ImageFilter.GaussianBlur(radius=radius))

    def createAvatar(self):
        size = self._basemapSize
        res = self.avatar
        self._img = self.resize(Image.open(BytesIO(res)).convert("RGBA"), (size, size))
        return self

    def createRoundImg(self):
        img = self._img
        size = self.avatarSize

        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        self._roundImg = self.resize(img, (size, size))
        self._roundImg.putalpha(mask)
        return self

    def createCanvas(self):
        size = self._basemapSize
        self._canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self._canvas.paste(self.gaussianBlur(self._img))
        return self

    def createAMagicCircle(self):
        size = self._magicCirclePlus + self.avatarSize
        magicCircle = Image.open(f"{RESOURCES_BASE_PATH}/magic-circle.png").convert("L")
        magicCircle = self.resize(magicCircle, (size, size))
        self._magicCircle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self._magicCircle.putalpha(magicCircle)
        return self

    def createTextBasemap(self, transparency=190):
        self._textBaseMap = Image.new(
            "RGBA", self._textBaseMapSize, (0, 0, 0, transparency)
        )
        self._textBaseMap = self.imageRadiusProcessing(self._textBaseMap, transparency)
        return self

    def additionalMagicCircle(self):
        magicCircle = self._magicCircle
        x = int((self._basemapSize - self.avatarSize - self._magicCirclePlus) / 2)
        y = x - self._avatarVerticalOffset
        self._canvas.paste(magicCircle, (x, y), magicCircle)
        return self

    def additionalAvatar(self):
        avatar = self._roundImg
        x = int((self._basemapSize - self.avatarSize) / 2)
        y = x - self._avatarVerticalOffset
        self._canvas.paste(avatar, (x, y), avatar)
        return self

    def additionalTextBaseMap(self):
        textBaseMap = self._textBaseMap
        x = int((self._basemapSize - self._textBaseMapSize[0]) / 2)
        y = self._topPositionOfTextBaseMap
        self._canvas.paste(textBaseMap, (x, y), textBaseMap)
        return self

    def writePicture(
        self, img, text, position, fontName, fontSize, color=(255, 255, 255)
    ):
        font = ImageFont.truetype(f"{RESOURCES_BASE_PATH}/font/{fontName}", fontSize)
        draw = ImageDraw.Draw(img)
        textSize = font.getsize(text)
        attenuation = self._fontAttenuation
        x = int(position[0] - textSize[0] / 2)
        limit = self._minimumFontLimit
        while x <= self._textBaseMapLeftPosition:
            fontSize -= attenuation
            if fontSize <= limit:
                return False
            font = ImageFont.truetype(
                f"{RESOURCES_BASE_PATH}/font/{fontName}", fontSize
            )
            textSize = font.getsize(text)
            x = int(position[0] - textSize[0] / 2)
        y = int(position[1] - textSize[1] / 2)
        draw.text((x, y), text, color, font=font)
        return True

    def additionalSignInInformation(self):
        fontSize = self._infoFontSize
        coordinateY = self._infoCoordinatesY
        font = self._infoFontName
        x = int(self._basemapSize / 2)
        # Add user nickname
        result = self.writePicture(
            img=self._canvas,
            text=self.nickname,
            position=(x, coordinateY.nickname),
            fontName=font.nickname,
            fontSize=fontSize.nickname,
        )
        if not result:
            return False
        # Add success message
        result = self.writePicture(
            img=self._canvas,
            text=self._userInfo,
            position=(x, coordinateY.info),
            fontName=font.info,
            fontSize=fontSize.info,
        )
        if result is False:
            return False
        # Add integration information
        result = self.writePicture(
            img=self._canvas,
            text=self._userInfoIntegration,
            position=(x, coordinateY.integration),
            fontName=font.integration,
            fontSize=fontSize.integration,
        )
        if not result:
            return result
        # Addition hitokoto
        result = self.writePicture(
            img=self._canvas,
            text=self.hitokoto,
            position=(x, coordinateY.hitokoto),
            fontName=font.hitokoto,
            fontSize=fontSize.hitokoto,
        )
        if not result:
            return result
        return self

    def get_bytes(self):
        with BytesIO() as f:
            self._canvas.save(f, "PNG")
            return f.getvalue()
