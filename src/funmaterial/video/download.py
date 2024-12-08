import hashlib
import json
import os
import random
from typing import List
from urllib.parse import urlencode

import requests
from funfake.headers import fake_header
from funget import simple_download
from funmaterial.api.pixabay import PixabayAPI
from funmaterial.schema import VideoInfo, ProviderType
from funmaterial.video.schema import VideoAspect, VideoConcatMode
from funutil import getLogger
from moviepy.video.io.VideoFileClip import VideoFileClip

logger = getLogger("funmaterial")


def save_video(video_url: str, save_dir: str = "", *args, **kwargs) -> str:
    os.makedirs(save_dir, exist_ok=True)
    url_without_query = video_url.split("?")[0]
    url_hash = hashlib.md5(url_without_query.encode("utf-8")).hexdigest()
    video_path = f"{save_dir}/vid-{url_hash}.mp4"
    simple_download(url=video_url, filepath=video_path, overwrite=False)

    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            fps = clip.fps
            clip.close()
            if duration > 0 and fps > 0:
                return video_path
        except Exception as e:
            try:
                os.remove(video_path)
            except Exception as e:
                logger.error(f"failed to remove {video_path}: {e}")
            logger.warning(f"invalid video file: {video_path} => {e}")
    return ""


class MaterialEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def search_video(
        self,
        search_term: str,
        minimum_duration: int,
        proxy=None,
        video_aspect: VideoAspect = VideoAspect.portrait,
        *args,
        **kwargs,
    ) -> List[VideoInfo]:
        pass

    def download_videos(
        self,
        search_terms: List[str],
        material_directory="./material",
        video_aspect: VideoAspect = VideoAspect.portrait,
        video_contact_mode: VideoConcatMode = VideoConcatMode.random,
        audio_duration: float = 0.0,
        max_clip_duration: int = 5,
    ) -> List[str]:
        valid_video_items = []
        valid_video_urls = []
        found_duration = 0.0

        for search_term in search_terms:
            video_items = self.search_video(
                search_term=search_term,
                minimum_duration=max_clip_duration,
                video_aspect=video_aspect,
            )
            logger.info(f"found {len(video_items)} videos for '{search_term}'")

            for item in video_items:
                if item.url not in valid_video_urls:
                    valid_video_items.append(item)
                    valid_video_urls.append(item.url)
                    found_duration += item.duration

        logger.info(
            f"found total videos: {len(valid_video_items)}, required duration: {audio_duration} seconds, found duration: {found_duration} seconds"
        )
        video_paths = []
        os.makedirs(material_directory, exist_ok=True)

        if video_contact_mode.value == VideoConcatMode.random.value:
            random.shuffle(valid_video_items)

        total_duration = 0.0
        for item in valid_video_items:
            try:
                logger.info(f"downloading video: {item.url}")
                saved_video_path = save_video(
                    video_url=item.url, save_dir=material_directory
                )
                if saved_video_path:
                    logger.info(f"video saved: {saved_video_path}")
                    video_paths.append(saved_video_path)
                    seconds = min(max_clip_duration, item.duration)
                    total_duration += seconds
                    if total_duration > audio_duration:
                        logger.info(
                            f"total duration of downloaded videos: {total_duration} seconds, skip downloading more"
                        )
                        break
            except Exception as e:
                logger.error(f"failed to download video: {to_json(item)} => {str(e)}")
        logger.success(f"downloaded {len(video_paths)} videos")
        return video_paths


#
def to_json(obj):
    try:
        # 定义一个辅助函数来处理不同类型的对象
        def serialize(o):
            # 如果对象是可序列化类型，直接返回
            if isinstance(o, (int, float, bool, str)) or o is None:
                return o
            # 如果对象是二进制数据，转换为base64编码的字符串
            elif isinstance(o, bytes):
                return "*** binary data ***"
            # 如果对象是字典，递归处理每个键值对
            elif isinstance(o, dict):
                return {k: serialize(v) for k, v in o.items()}
            # 如果对象是列表或元组，递归处理每个元素
            elif isinstance(o, (list, tuple)):
                return [serialize(item) for item in o]
            # 如果对象是自定义类型，尝试返回其__dict__属性
            elif hasattr(o, "__dict__"):
                return serialize(o.__dict__)
            # 其他情况返回None（或者可以选择抛出异常）
            else:
                return None

        # 使用serialize函数处理输入对象
        serialized_obj = serialize(obj)

        # 序列化处理后的对象为JSON字符串
        return json.dumps(serialized_obj, ensure_ascii=False, indent=4)
    except Exception as e:
        return None


class PexelsEngine(MaterialEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def search_video(
        self,
        search_term: str,
        minimum_duration: int,
        proxy=None,
        video_aspect: VideoAspect = VideoAspect.portrait,
        *args,
        **kwargs,
    ) -> List[VideoInfo]:
        aspect = VideoAspect(video_aspect)
        video_orientation = aspect.name
        video_width, video_height = aspect.to_resolution()
        headers = fake_header()
        headers["Authorization"] = self.api_key

        # Build URL
        params = {
            "query": search_term,
            "per_page": 20,
            "orientation": video_orientation,
        }
        query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
        logger.info(f"searching videos: {query_url}, with proxies: {proxy}")

        try:
            r = requests.get(
                query_url,
                headers=headers,
                proxies=proxy,
                verify=False,
                timeout=(30, 60),
            )
            response = r.json()
            video_items = []
            if "videos" not in response:
                logger.error(f"search videos failed: {response}")
                return video_items
            videos = response["videos"]
            # loop through each video in the result
            for v in videos:
                duration = v["duration"]
                # check if video has desired minimum duration
                if duration < minimum_duration:
                    continue
                video_files = v["video_files"]
                # loop through each url to determine the best quality
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
            return video_items
        except Exception as e:
            logger.error(f"search videos failed: {str(e)}")

        return []


class PixabayEngine(MaterialEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def search_video(
        self,
        search_term: str,
        minimum_duration: int,
        proxy=None,
        video_aspect: VideoAspect = VideoAspect.portrait,
        video_type="all",
        per_page=50,
        *args,
        **kwargs,
    ) -> List[VideoInfo]:
        aspect = VideoAspect(video_aspect)
        video_width, video_height = aspect.to_resolution()

        try:
            response = PixabayAPI(api_key=self.api_key).search_video(
                q=search_term, video_type=video_type, per_page=per_page
            )
            video_items = []
            if "hits" not in response:
                logger.error(f"search videos failed: {response}")
                return video_items
            videos = response["hits"]
            # loop through each video in the result
            for v in videos:
                duration = v["duration"]
                # check if video has desired minimum duration
                if duration < minimum_duration:
                    continue
                video_files = v["videos"]
                # loop through each url to determine the best quality
                for video_type in video_files:
                    video = video_files[video_type]
                    w = int(video["width"])
                    h = int(video["height"])
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
        except Exception as e:
            logger.error(f"search videos failed: {str(e)}")

        return []


def download_videos(
    api_key: str,
    search_terms: List[str],
    source: str = "pexels",
    material_directory="./material/video",
    video_aspect: VideoAspect = VideoAspect.portrait,
    video_contact_mode: VideoConcatMode = VideoConcatMode.random,
    audio_duration: float = 0.0,
    max_clip_duration: int = 5,
) -> List[str]:
    engine = None
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


if __name__ == "__main__":
    engine = PixabayEngine()
    for record in engine.search_video(
        search_term="Money Exchange Medium", minimum_duration=10
    ):
        print(record)
