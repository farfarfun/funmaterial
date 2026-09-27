from enum import Enum


class MaterialType(Enum):
    """素材类型枚举。"""

    IMAGE = 101
    AUDIO = 102
    VIDEO = 103


class ProviderType(Enum):
    """素材提供方枚举。"""

    PEXELS = 201
    PIXABAY = 202


class MaterialInfo(dict):
    """素材信息的基础字典结构。"""

    def __init__(
        self,
        type: MaterialType,
        provider: ProviderType,
        url: str,
        *args: object,
        **kwargs: object,
    ) -> None:
        """初始化素材信息。

        Args:
            type: 素材类型。
            provider: 素材提供方。
            url: 素材地址。
            *args: 传递给字典的额外位置参数。
            **kwargs: 传递给字典的额外字段。
        """
        super().__init__(type=type, url=url, *args, **kwargs)
        self.provider = provider
        self.type = type
        self.url = url


class VideoInfo(MaterialInfo):
    """视频素材信息。"""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """初始化视频素材信息。"""
        super().__init__(type=MaterialType.VIDEO, *args, **kwargs)
        self.duration: int = 0


class AudioInfo(MaterialInfo):
    """音频素材信息。"""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """初始化音频素材信息。"""
        super().__init__(type=MaterialType.AUDIO, *args, **kwargs)


class ImageInfo(MaterialInfo):
    """图片素材信息。"""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """初始化图片素材信息。"""
        super().__init__(type=MaterialType.IMAGE, *args, **kwargs)
