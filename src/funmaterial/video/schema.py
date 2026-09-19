from __future__ import annotations

from enum import Enum

import pydantic

_CONFIG = pydantic.ConfigDict(arbitrary_types_allowed=True)


@pydantic.dataclasses.dataclass(config=_CONFIG)
class MaterialInfo:
    """素材基础信息。"""

    provider: str = "pexels"
    url: str = ""
    duration: int = 0


class VideoAspect(str, Enum):
    """视频画面比例。"""

    landscape = "16:9"
    portrait = "9:16"
    square = "1:1"

    def to_resolution(self) -> tuple[int, int]:
        """将画面比例换算为目标分辨率。

        Returns:
            `(宽, 高)` 像素分辨率元组；无法识别的取值回退为竖屏 `(1080, 1920)`。
        """
        if self == VideoAspect.landscape.value:
            return 1920, 1080
        elif self == VideoAspect.portrait.value:
            return 1080, 1920
        elif self == VideoAspect.square.value:
            return 1080, 1080
        return 1080, 1920


class VideoConcatMode(str, Enum):
    """多段视频的拼接方式。"""

    random = "random"
    sequential = "sequential"
