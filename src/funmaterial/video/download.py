from __future__ import annotations

import hashlib
import json
import os
import random
from typing import Any
from urllib.parse import urlencode

import requests
from farlog import getLogger
from funfake.headers import fake_header
from funget import simple_download
from moviepy.video.io.VideoFileClip import VideoFileClip

from funmaterial.api.pixabay import PixabayAPI
from funmaterial.exceptions import MaterialAPIError, MaterialSearchError
from funmaterial.schema import ProviderType, VideoInfo
from funmaterial.video.schema import VideoAspect, VideoConcatMode

logger = getLogger("funmaterial")


def save_video(video_url: str, save_dir: str = "", *args: Any, **kwargs: Any) -> str:
    """下载单个视频并校验其有效性。

    使用 `moviepy` 打开下载后的文件，确认时长、帧率均大于 0；校验失败的文件会被删除。

    Args:
        video_url: 视频下载地址。
        save_dir: 保存目录，会自动创建。

    Returns:
        校验通过后的本地文件路径；下载失败或视频文件无效时返回空字符串。
    """
    os.makedirs(save_dir, exist_ok=True)
    url_without_query = video_url.split("?")[0]
    url_hash = hashlib.md5(url_without_query.encode("utf-8")).hexdigest()
    video_path = f"{save_dir}/vid-{url_hash}.mp4"
    try:
        simple_download(url=video_url, filepath=video_path, overwrite=False)
    except Exception as e:  # noqa: BLE001 -- 下载器未定义稳定的异常层级
        logger.warning(
            "failed to download video: url={}, path={}, error={}",
            video_url,
            video_path,
            e,
        )
        return ""

    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            fps = clip.fps
            clip.close()
            if duration > 0 and fps > 0:
                return video_path
        except Exception as e:  # noqa: BLE001 -- moviepy 对损坏文件抛出的异常类型不固定，此处需要兜底
            try:
                os.remove(video_path)
            except OSError as remove_error:
                logger.error("failed to remove {}: {}", video_path, remove_error)
            logger.warning("invalid video file: {} => {}", video_path, e)
    return ""


class MaterialEngine:
    """素材搜索引擎的基类，定义统一的搜索 / 批量下载接口。"""

    def __init__(self, api_key: str | None = None) -> None:
        """初始化引擎。

        Args:
            api_key: 目标素材服务的 API key。
        """
        self.api_key = api_key

    def search_video(
        self,
        search_term: str,
        minimum_duration: int,
        proxy: dict[str, str] | None = None,
        video_aspect: VideoAspect = VideoAspect.portrait,
        *args: Any,
        **kwargs: Any,
    ) -> list[VideoInfo]:
        """搜索视频素材，子类必须实现。

        Args:
            search_term: 搜索关键词。
            minimum_duration: 最短时长（秒），短于该时长的结果会被过滤。
            proxy: 请求代理配置。
            video_aspect: 目标画面比例，用于筛选合适分辨率的素材。

        Returns:
            匹配的视频信息列表。

        Raises:
            NotImplementedError: 基类未实现具体的搜索逻辑，必须由子类覆盖。
        """
        raise NotImplementedError(
            f"{type(self).__name__} 未实现 search_video，请使用具体的引擎子类"
            "（如 PexelsEngine / PixabayEngine）"
        )

    def download_videos(
        self,
        search_terms: list[str],
        material_directory: str = "./material",
        video_aspect: VideoAspect = VideoAspect.portrait,
        video_contact_mode: VideoConcatMode = VideoConcatMode.random,
        audio_duration: float = 0.0,
        max_clip_duration: int = 5,
    ) -> list[str]:
        """按关键词批量搜索并下载视频，直到累计时长满足要求。

        单个关键词搜索失败时记录带上下文的警告并跳过，不影响其余关键词。

        Args:
            search_terms: 搜索关键词列表。
            material_directory: 视频保存目录。
            video_aspect: 目标画面比例。
            video_contact_mode: 拼接顺序，random 时会打乱候选素材顺序。
            audio_duration: 目标音频时长（秒），累计视频时长超过该值即停止下载。
            max_clip_duration: 单个片段最长使用时长（秒）。

        Returns:
            成功下载并通过校验的本地视频文件路径列表。
        """
        valid_video_items: list[VideoInfo] = []
        valid_video_urls: list[str] = []
        found_duration = 0.0

        for search_term in search_terms:
            try:
                video_items = self.search_video(
                    search_term=search_term,
                    minimum_duration=max_clip_duration,
                    video_aspect=video_aspect,
                )
            except MaterialSearchError as e:
                logger.warning("skip search term due to search failure: {}", e)
                continue
            logger.info("found {} videos for '{}'", len(video_items), search_term)

            for item in video_items:
                if item.url not in valid_video_urls:
                    valid_video_items.append(item)
                    valid_video_urls.append(item.url)
                    found_duration += item.duration

        logger.info(
            "found total videos: {}, required duration: {} seconds, found duration: {} seconds",
            len(valid_video_items),
            audio_duration,
            found_duration,
        )
        video_paths = []
        os.makedirs(material_directory, exist_ok=True)

        if video_contact_mode.value == VideoConcatMode.random.value:
            random.shuffle(valid_video_items)

        total_duration = 0.0
        for item in valid_video_items:
            logger.info("downloading video: {}", item.url)
            saved_video_path = save_video(
                video_url=item.url, save_dir=material_directory
            )
            if saved_video_path:
                logger.info("video saved: {}", saved_video_path)
                video_paths.append(saved_video_path)
                seconds = min(max_clip_duration, item.duration)
                total_duration += seconds
                if total_duration > audio_duration:
                    logger.info(
                        "total duration of downloaded videos: {} seconds, skip downloading more",
                        total_duration,
                    )
                    break
        logger.success("downloaded {} videos", len(video_paths))
        return video_paths


def to_json(obj: Any) -> str:
    """将任意对象尽量序列化为可读的 JSON 字符串，主要用于日志输出。

    仅用于诊断信息展示：序列化失败时不会抛出异常打断调用方，而是记录
    带上下文（对象类型）的警告日志，并返回该对象的 `repr` 作为兜底。

    Args:
        obj: 待序列化的对象，支持基础类型、`bytes`、`dict`、`list`/`tuple`
            及拥有 `__dict__` 属性的自定义对象。

    Returns:
        JSON 字符串；序列化失败时返回 `repr(obj)`。
    """

    def serialize(o: Any) -> Any:
        # 如果对象是可序列化类型，直接返回
        if isinstance(o, (int, float, bool, str)) or o is None:
            return o
        # 如果对象是二进制数据，避免把原始字节写进日志
        elif isinstance(o, bytes):
            return "*** binary data ***"
        # 如果对象是字典，递归处理每个键值对
        elif isinstance(o, dict):
            return {k: serialize(v) for k, v in o.items()}
        # 如果对象是列表或元组，递归处理每个元素
        elif isinstance(o, (list, tuple)):
            return [serialize(item) for item in o]
        # 如果对象是自定义类型，尝试返回其 __dict__ 属性
        elif hasattr(o, "__dict__"):
            return serialize(o.__dict__)
        # 其他无法识别的类型：不能静默转换为 JSON null，否则会丢失原始值，
        # 返回可定位的 repr 兜底
        else:
            return repr(o)

    try:
        serialized_obj = serialize(obj)
        return json.dumps(serialized_obj, ensure_ascii=False, indent=4)
    except (TypeError, ValueError) as e:
        logger.warning("failed to serialize object of type {!r}: {}", type(obj), e)
        return repr(obj)


class PexelsEngine(MaterialEngine):
    """基于 Pexels 的视频素材搜索引擎。"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def search_video(
        self,
        search_term: str,
        minimum_duration: int,
        proxy: dict[str, str] | None = None,
        video_aspect: VideoAspect = VideoAspect.portrait,
        *args: Any,
        **kwargs: Any,
    ) -> list[VideoInfo]:
        """在 Pexels 上搜索视频素材。

        Args:
            search_term: 搜索关键词。
            minimum_duration: 最短时长（秒），短于该时长的结果会被过滤。
            proxy: 请求代理配置。
            video_aspect: 目标画面比例，用于筛选合适分辨率的素材。

        Returns:
            匹配的视频信息列表。

        Raises:
            MaterialSearchError: 请求失败或响应格式不符合预期时抛出，携带
                搜索词、URL 等上下文。
        """
        aspect = VideoAspect(video_aspect)
        video_orientation = aspect.name
        video_width, video_height = aspect.to_resolution()
        headers = fake_header()
        headers["Authorization"] = self.api_key

        # 构造请求地址
        params = {
            "query": search_term,
            "per_page": 20,
            "orientation": video_orientation,
        }
        query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
        logger.info("searching videos: {}, with proxies: {}", query_url, proxy)

        try:
            r = requests.get(
                query_url,
                headers=headers,
                proxies=proxy,
                verify=False,
                timeout=(30, 60),
            )
        except requests.RequestException as e:
            raise MaterialSearchError(
                "Pexels 视频搜索请求异常",
                service="pexels",
                search_term=search_term,
                url=query_url,
            ) from e

        if r.status_code < 200 or r.status_code >= 300:
            raise MaterialSearchError(
                f"Pexels 视频搜索请求失败: {r.text}",
                service="pexels",
                search_term=search_term,
                url=query_url,
                status_code=r.status_code,
            )

        try:
            response = r.json()
        except ValueError as e:
            raise MaterialSearchError(
                "Pexels 视频搜索响应不是合法 JSON",
                service="pexels",
                search_term=search_term,
                url=query_url,
                status_code=r.status_code,
            ) from e

        if not isinstance(response, dict) or not isinstance(
            response.get("videos"), list
        ):
            raise MaterialSearchError(
                f"Pexels 视频搜索响应缺少 videos 字段: {response}",
                service="pexels",
                search_term=search_term,
                url=query_url,
                status_code=r.status_code,
            )

        try:
            video_items = []
            videos = response["videos"]
            # 遍历搜索结果中的视频
            for v in videos:
                duration = v["duration"]
                # 过滤掉时长不足的视频
                if duration < minimum_duration:
                    continue
                video_files = v["video_files"]
                # 遍历视频地址并选择合适的画质
                for video in video_files:
                    w = int(video["width"])
                    h = int(video["height"])
                    if w == video_width and h == video_height:
                        item = VideoInfo(
                            provider=ProviderType.PEXELS,
                            url=video["link"],
                            duration=duration,
                        )
                        video_items.append(item)
                        break
        except (KeyError, TypeError, ValueError) as e:
            raise MaterialSearchError(
                "Pexels 视频搜索响应格式不符合预期",
                service="pexels",
                search_term=search_term,
                url=query_url,
                status_code=r.status_code,
            ) from e
        return video_items


class PixabayEngine(MaterialEngine):
    """基于 Pixabay 的视频素材搜索引擎。"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def search_video(
        self,
        search_term: str,
        minimum_duration: int,
        proxy: dict[str, str] | None = None,
        video_aspect: VideoAspect = VideoAspect.portrait,
        video_type: str = "all",
        per_page: int = 50,
        *args: Any,
        **kwargs: Any,
    ) -> list[VideoInfo]:
        """在 Pixabay 上搜索视频素材。

        Args:
            search_term: 搜索关键词。
            minimum_duration: 最短时长（秒），短于该时长的结果会被过滤。
            proxy: 请求代理配置（当前未使用，保留接口一致性）。
            video_aspect: 目标画面比例，用于筛选合适分辨率的素材。
            video_type: Pixabay 视频类型过滤，"all" / "film" / "animation"。
            per_page: 每页结果数。

        Returns:
            匹配的视频信息列表。

        Raises:
            MaterialSearchError: 请求失败或响应格式不符合预期时抛出，携带
                搜索词等上下文。
        """
        aspect = VideoAspect(video_aspect)
        video_width, _video_height = aspect.to_resolution()

        try:
            response = PixabayAPI(api_key=self.api_key).search_video(
                q=search_term, video_type=video_type, per_page=per_page
            )
        except (MaterialAPIError, requests.RequestException) as e:
            raise MaterialSearchError(
                "Pixabay 视频搜索请求异常",
                service="pixabay",
                search_term=search_term,
            ) from e

        if "hits" not in response:
            raise MaterialSearchError(
                f"Pixabay 视频搜索响应缺少 hits 字段: {response}",
                service="pixabay",
                search_term=search_term,
            )

        video_items = []
        videos = response["hits"]
        # 遍历搜索结果中的视频
        for v in videos:
            duration = v["duration"]
            # 过滤掉时长不足的视频
            if duration < minimum_duration:
                continue
            video_files = v["videos"]
            # 遍历视频地址并选择合适的画质
            for quality in video_files:
                video = video_files[quality]
                w = int(video["width"])
                if w >= video_width:
                    video_items.append(
                        VideoInfo(
                            provider=ProviderType.PIXABAY,
                            duration=duration,
                            url=video["url"],
                            height=video["height"],
                            width=video["width"],
                            size=video["size"],
                            thumbnail=video["thumbnail"],
                            views=v["views"],
                            downloads=v["downloads"],
                            likes=v["likes"],
                            comments=v["comments"],
                            user_id=v["user_id"],
                            user=v["user"],
                            tags=v["tags"],
                        )
                    )
                    break
        return video_items


def download_videos(
    api_key: str,
    search_terms: list[str],
    source: str = "pexels",
    material_directory: str = "./material/video",
    video_aspect: VideoAspect = VideoAspect.portrait,
    video_contact_mode: VideoConcatMode = VideoConcatMode.random,
    audio_duration: float = 0.0,
    max_clip_duration: int = 5,
) -> list[str] | None:
    """按来源批量搜索并下载视频素材。

    Args:
        api_key: 目标素材服务的 API key。
        search_terms: 搜索关键词列表。
        source: 素材来源，支持 "pexels" 或 "pixabay"。
        material_directory: 视频保存目录。
        video_aspect: 目标画面比例。
        video_contact_mode: 拼接顺序，random 时会打乱候选素材顺序。
        audio_duration: 目标音频时长（秒），累计视频时长超过该值即停止下载。
        max_clip_duration: 单个片段最长使用时长（秒）。

    Returns:
        成功下载并通过校验的本地视频文件路径列表；`source` 不受支持时返回 `None`。
    """
    engine: MaterialEngine | None = None
    if source == "pexels":
        engine = PexelsEngine(api_key=api_key)
    elif source == "pixabay":
        engine = PixabayEngine(api_key=api_key)
    if engine is not None:
        return engine.download_videos(
            search_terms=search_terms,
            material_directory=material_directory,
            video_aspect=video_aspect,
            video_contact_mode=video_contact_mode,
            max_clip_duration=max_clip_duration,
            audio_duration=audio_duration,
        )
    return None


if __name__ == "__main__":
    engine = PixabayEngine()
    for record in engine.search_video(
        search_term="Money Exchange Medium", minimum_duration=10
    ):
        logger.info(to_json(record))
