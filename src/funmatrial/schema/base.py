from enum import Enum


class MaterialType(Enum):
    IMAGE = 101
    AUDIO = 102
    VIDEO = 103


class ProviderType(Enum):
    PEXELS = 201
    PIXABAY = 202


class MaterialInfo(dict):
    def __init__(self, type, provider, url, *args, **kwargs):
        super().__init__(type=type, url=url, *args, **kwargs)
        self.provider = provider
        self.type = type
        self.url = url


class VideoInfo(MaterialInfo):
    def __init__(self, *args, **kwargs):
        super().__init__(type=MaterialType.VIDEO, *args, **kwargs)
        self.duration: int = 0


class AudioInfo(MaterialInfo):
    def __init__(self, *args, **kwargs):
        super().__init__(type=MaterialType.AUDIO, *args, **kwargs)


class ImageInfo(MaterialInfo):
    def __init__(self, *args, **kwargs):
        super().__init__(type=MaterialType.IMAGE, *args, **kwargs)
