"""funmaterial 冒烟测试。

funmaterial 从 Zenodo、Pexels、Pixabay 和 Unsplash 获取背景音乐、字体、库存视频和图片。
这些测试不会访问真实网络，所有 HTTP 和远程驱动调用都使用 ``unittest.mock`` 模拟。

编写本测试时，``audio`` 和 ``picture`` 子模块仍是空桩模块，因此只检查它们能否导入。
"""

from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# 导入测试
# ---------------------------------------------------------------------------


def test_import_top_level_package():
    import funmaterial

    assert funmaterial is not None


@pytest.mark.parametrize(
    "module_name",
    [
        "funmaterial.audio",
        "funmaterial.picture",
    ],
)
def test_import_stub_submodules(module_name):
    """确认当前为空桩模块的 audio/picture 子模块可以导入。"""
    import importlib

    module = importlib.import_module(module_name)
    assert module is not None


@pytest.mark.parametrize(
    "module_name",
    [
        "funmaterial.schema",
        "funmaterial.exceptions",
        "funmaterial.api",
        "funmaterial.api.pixabay",
        "funmaterial.api.unsplash",
        "funmaterial.font",
        "funmaterial.font.zenodo",
        "funmaterial.song",
        "funmaterial.song.zenodo",
        "funmaterial.video",
        "funmaterial.video.download",
        "funmaterial.video.schema",
    ],
)
def test_import_real_submodules(module_name):
    import importlib

    module = importlib.import_module(module_name)
    assert module is not None


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


def test_schema_material_info_types():
    from funmaterial.schema import (
        AudioInfo,
        ImageInfo,
        MaterialType,
        ProviderType,
        VideoInfo,
    )

    video = VideoInfo(provider=ProviderType.PEXELS, url="http://example.com/v.mp4")
    assert video.type == MaterialType.VIDEO
    assert video.url == "http://example.com/v.mp4"
    assert video.duration == 0

    audio = AudioInfo(provider=ProviderType.PIXABAY, url="http://example.com/a.mp3")
    assert audio.type == MaterialType.AUDIO

    image = ImageInfo(provider=ProviderType.PIXABAY, url="http://example.com/i.jpg")
    assert image.type == MaterialType.IMAGE


def test_video_aspect_to_resolution():
    from funmaterial.video.schema import VideoAspect, VideoConcatMode

    assert VideoAspect.portrait.to_resolution() == (1080, 1920)
    assert VideoAspect.landscape.to_resolution() == (1920, 1080)
    assert VideoAspect.square.to_resolution() == (1080, 1080)
    assert VideoConcatMode.random.value == "random"


# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


def test_material_api_error_message_contains_context():
    from funmaterial.exceptions import MaterialAPIError

    err = MaterialAPIError(
        "boom", service="pixabay", url="http://x/api", status_code=403
    )
    assert "pixabay" in str(err)
    assert "http://x/api" in str(err)
    assert "403" in str(err)
    assert err.service == "pixabay"
    assert err.url == "http://x/api"
    assert err.status_code == 403


def test_material_search_error_message_contains_search_term():
    from funmaterial.exceptions import MaterialSearchError

    err = MaterialSearchError(
        "boom", service="pexels", search_term="cat", status_code=500
    )
    assert "cat" in str(err)
    assert "pexels" in str(err)
    assert err.search_term == "cat"


# ---------------------------------------------------------------------------
# Pixabay API（基于 requests）
# ---------------------------------------------------------------------------


def test_pixabay_search_image_mocked():
    from funmaterial.api.pixabay import PixabayAPI

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"hits": [{"id": 1, "tags": "cat"}]}

    with patch("funmaterial.api.pixabay.get", return_value=fake_response) as mock_get:
        api = PixabayAPI(api_key="fake-key")
        result = api.search_image(q="cat")

    mock_get.assert_called_once()
    _called_args, called_kwargs = mock_get.call_args
    assert called_kwargs["params"]["key"] == "fake-key"
    assert called_kwargs["params"]["q"] == "cat"
    assert result == {"hits": [{"id": 1, "tags": "cat"}]}


def test_pixabay_search_video_mocked():
    from funmaterial.api.pixabay import PixabayAPI

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"hits": [{"id": 2, "duration": 10}]}

    with patch("funmaterial.api.pixabay.get", return_value=fake_response) as mock_get:
        api = PixabayAPI(api_key="fake-key")
        result = api.search_video(q="dog")

    mock_get.assert_called_once()
    assert result["hits"][0]["duration"] == 10


def test_pixabay_search_image_error_raises_material_api_error():
    from funmaterial.api.pixabay import PixabayAPI
    from funmaterial.exceptions import MaterialAPIError

    fake_response = MagicMock()
    fake_response.status_code = 403
    fake_response.text = "Forbidden"
    fake_response.url = "http://pixabay.example/api/?q=cat"

    with patch("funmaterial.api.pixabay.get", return_value=fake_response):
        api = PixabayAPI(api_key="fake-key")
        with pytest.raises(MaterialAPIError) as exc_info:
            api.search_image(q="cat")

    err = exc_info.value
    assert err.service == "pixabay"
    assert err.status_code == 403
    assert "Forbidden" in str(err)


def test_pixabay_search_video_error_raises_material_api_error():
    from funmaterial.api.pixabay import PixabayAPI
    from funmaterial.exceptions import MaterialAPIError

    fake_response = MagicMock()
    fake_response.status_code = 500
    fake_response.text = "Internal Server Error"
    fake_response.url = "http://pixabay.example/api/videos/?q=dog"

    with patch("funmaterial.api.pixabay.get", return_value=fake_response):
        api = PixabayAPI(api_key="fake-key")
        with pytest.raises(MaterialAPIError) as exc_info:
            api.search_video(q="dog")

    assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# Unsplash API（基于 requests）
# ---------------------------------------------------------------------------


def test_unsplash_list_photos_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [{"id": "abc123"}]

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.list_photos(page=2, per_page=5)

    mock_get.assert_called_once()
    _called_args, called_kwargs = mock_get.call_args
    assert called_kwargs["params"]["client_id"] == "fake-access"
    assert called_kwargs["params"]["page"] == 2
    assert result == [{"id": "abc123"}]


def test_unsplash_get_photo_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": "photo-1"}

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.get_photo("photo-1")

    mock_get.assert_called_once()
    assert result == {"id": "photo-1"}


def test_unsplash_search_photos_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"results": []}

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.search_photos(query="mountain")

    mock_get.assert_called_once()
    assert result == {"results": []}


def test_unsplash_get_photo_random_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": "random-photo"}

    with patch("funmaterial.api.unsplash.requests.get", return_value=fake_response):
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.get_photo_random(query="sea")

    assert result == {"id": "random-photo"}


def test_unsplash_search_collection_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"results": ["collection-1"]}

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.search_collection(query="nature")

    mock_get.assert_called_once()
    assert result == {"results": ["collection-1"]}


def test_unsplash_search_users_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"results": ["user-1"]}

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.search_users(query="jane")

    mock_get.assert_called_once()
    assert result == {"results": ["user-1"]}


def test_unsplash_list_topic_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [{"id": "topic-1"}]

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.list_topic()

    mock_get.assert_called_once()
    assert result == [{"id": "topic-1"}]


def test_unsplash_topic_detail_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": "topic-1", "slug": "nature"}

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.topic_detail(slug="nature")

    mock_get.assert_called_once()
    assert result["slug"] == "nature"


def test_unsplash_topic_photos_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [{"id": "photo-1"}]

    with patch(
        "funmaterial.api.unsplash.requests.get", return_value=fake_response
    ) as mock_get:
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        result = client.topic_photos(slug="nature")

    mock_get.assert_called_once()
    assert result == [{"id": "photo-1"}]


def test_unsplash_stats_total_and_month_mocked():
    from funmaterial.api.unsplash import Unsplash

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"photos": 1}

    with patch("funmaterial.api.unsplash.requests.get", return_value=fake_response):
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        assert client.stats_total() == {"photos": 1}
        assert client.stats_month() == {"photos": 1}


def test_unsplash_get_raises_material_api_error_on_http_error():
    from funmaterial.api.unsplash import Unsplash
    from funmaterial.exceptions import MaterialAPIError

    fake_response = MagicMock()
    fake_response.status_code = 403
    fake_response.text = "Forbidden"
    fake_response.url = "https://api.unsplash.com/photos"

    with patch("funmaterial.api.unsplash.requests.get", return_value=fake_response):
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        with pytest.raises(MaterialAPIError) as exc_info:
            client.list_photos()

    assert exc_info.value.service == "unsplash"
    assert exc_info.value.status_code == 403


def test_unsplash_get_raises_material_api_error_on_network_error():
    import requests

    from funmaterial.api.unsplash import Unsplash
    from funmaterial.exceptions import MaterialAPIError

    with patch(
        "funmaterial.api.unsplash.requests.get",
        side_effect=requests.ConnectionError("network down"),
    ):
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        with pytest.raises(MaterialAPIError) as exc_info:
            client.list_photos()

    assert exc_info.value.service == "unsplash"
    assert isinstance(exc_info.value.__cause__, requests.ConnectionError)


def test_unsplash_get_raises_material_api_error_on_invalid_json():
    from funmaterial.api.unsplash import Unsplash
    from funmaterial.exceptions import MaterialAPIError

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.side_effect = ValueError("not json")
    fake_response.url = "https://api.unsplash.com/photos"

    with patch("funmaterial.api.unsplash.requests.get", return_value=fake_response):
        client = Unsplash(access_key="fake-access", secret_key="fake-secret")
        with pytest.raises(MaterialAPIError) as exc_info:
            client.list_photos()

    assert exc_info.value.service == "unsplash"
    assert exc_info.value.status_code == 200


# ---------------------------------------------------------------------------
# 基于 Zenodo 的字体和歌曲获取器
# ---------------------------------------------------------------------------


def test_random_font_from_zenodo_mocked():
    from funmaterial.font import zenodo as font_zenodo

    fake_files = [
        {"path": "b.ttf", "url": "http://zenodo.example/b.ttf"},
        {"path": "a.ttf", "url": "http://zenodo.example/a.ttf"},
    ]

    with (
        patch.object(
            font_zenodo.drive, "get_file_list", return_value=fake_files
        ) as mock_list,
        patch.object(
            font_zenodo, "simple_download", return_value=None
        ) as mock_download,
    ):
        result = font_zenodo.random_font_from_zenodo(record_id=1234)

    mock_list.assert_called_once_with(record_id=1234)
    mock_download.assert_called_once()
    assert result.startswith("material/font/")
    assert result.endswith(".ttf")


def test_random_song_from_zenodo_mocked():
    from funmaterial.song import zenodo as song_zenodo

    fake_files = [
        {"path": "song1.mp3", "url": "http://zenodo.example/song1.mp3"},
    ]

    with (
        patch.object(
            song_zenodo.drive, "get_file_list", return_value=fake_files
        ) as mock_list,
        patch.object(
            song_zenodo, "simple_download", return_value=None
        ) as mock_download,
    ):
        result = song_zenodo.random_song_from_zenodo(record_id=5678)

    mock_list.assert_called_once_with(record_id=5678)
    mock_download.assert_called_once()
    assert result == "material/song/song1.mp3"


# ---------------------------------------------------------------------------
# JSON 序列化
# ---------------------------------------------------------------------------


def test_to_json_serializes_basic_types_and_nested_structures():
    from funmaterial.video.download import to_json

    result = to_json({"a": 1, "b": [1, "x", None, True], "c": {"d": b"bytes"}})
    assert '"a": 1' in result
    assert '"*** binary data ***"' in result


def test_to_json_serializes_custom_object_via_dict():
    from funmaterial.video.download import to_json

    class Custom:
        def __init__(self):
            self.x = 1
            self.y = "text"

    result = to_json(Custom())
    assert '"x": 1' in result
    assert '"y": "text"' in result


def test_to_json_uses_repr_for_unrecognized_object_instead_of_null():
    """不支持且没有 __dict__ 的对象应保留 repr，不能被静默转换成 JSON null。"""
    from funmaterial.video.download import to_json

    class NoDictSlots:
        __slots__ = ()

        def __repr__(self):
            return "<NoDictSlots marker>"

    unknown = NoDictSlots()
    result = to_json({"item": unknown})
    assert "<NoDictSlots marker>" in result
    assert "null" not in result


def test_to_json_falls_back_to_repr_on_serialization_failure():
    """验证 items() 抛出异常的字典子类会触发 to_json 的兜底路径。"""
    from funmaterial.video.download import to_json

    class BrokenDict(dict):
        def items(self):
            raise TypeError("broken mapping")

    obj = BrokenDict(a=1)
    result = to_json(obj)
    assert result == repr(obj)


# ---------------------------------------------------------------------------
# 保存视频
# ---------------------------------------------------------------------------


def test_save_video_returns_path_when_valid(tmp_path):
    from funmaterial.video import download as download_module

    fake_clip = MagicMock()
    fake_clip.duration = 12.0
    fake_clip.fps = 30.0

    def fake_download(url, filepath, overwrite=False):
        with open(filepath, "wb") as f:
            f.write(b"fake-video-bytes")

    with (
        patch.object(download_module, "simple_download", side_effect=fake_download),
        patch.object(download_module, "VideoFileClip", return_value=fake_clip),
    ):
        result = download_module.save_video(
            "http://x/video.mp4", save_dir=str(tmp_path)
        )

    assert result != ""
    assert result.startswith(str(tmp_path))


def test_save_video_removes_invalid_file_and_returns_empty(tmp_path):
    from funmaterial.video import download as download_module

    def fake_download(url, filepath, overwrite=False):
        with open(filepath, "wb") as f:
            f.write(b"not-a-real-video")

    with (
        patch.object(download_module, "simple_download", side_effect=fake_download),
        patch.object(
            download_module,
            "VideoFileClip",
            side_effect=OSError("cannot open corrupted file"),
        ),
    ):
        result = download_module.save_video(
            "http://x/video.mp4", save_dir=str(tmp_path)
        )

    assert result == ""
    remaining = list(tmp_path.glob("*.mp4"))
    assert remaining == []


def test_save_video_returns_empty_when_download_produces_no_file(tmp_path):
    from funmaterial.video import download as download_module

    with patch.object(download_module, "simple_download", return_value=None):
        result = download_module.save_video(
            "http://x/video.mp4", save_dir=str(tmp_path)
        )

    assert result == ""


# ---------------------------------------------------------------------------
# 视频下载引擎（Pexels / Pixabay）
# ---------------------------------------------------------------------------


def test_material_engine_base_search_video_raises_not_implemented():
    from funmaterial.video.download import MaterialEngine
    from funmaterial.video.schema import VideoAspect

    engine = MaterialEngine(api_key="fake")
    with pytest.raises(NotImplementedError):
        engine.search_video(
            search_term="cat", minimum_duration=1, video_aspect=VideoAspect.portrait
        )


def test_pexels_engine_search_video_mocked():
    from funmaterial.video.download import PexelsEngine
    from funmaterial.video.schema import VideoAspect

    fake_response = MagicMock()
    fake_response.json.return_value = {
        "videos": [
            {
                "duration": 20,
                "video_files": [
                    {"width": 1080, "height": 1920, "link": "http://x/v.mp4"}
                ],
            }
        ]
    }

    with patch(
        "funmaterial.video.download.requests.get", return_value=fake_response
    ) as mock_get:
        engine = PexelsEngine(api_key="fake-key")
        items = engine.search_video(
            search_term="cat",
            minimum_duration=5,
            video_aspect=VideoAspect.portrait,
        )

    mock_get.assert_called_once()
    assert len(items) == 1
    assert items[0].url == "http://x/v.mp4"
    # VideoInfo.duration 属性与字典值均应保留调用方传入的时长。
    assert items[0].duration == 20
    assert items[0]["duration"] == 20


def test_pexels_engine_search_video_raises_on_missing_videos_key():
    from funmaterial.exceptions import MaterialSearchError
    from funmaterial.video.download import PexelsEngine
    from funmaterial.video.schema import VideoAspect

    fake_response = MagicMock()
    fake_response.json.return_value = {"error": "bad request"}

    with patch("funmaterial.video.download.requests.get", return_value=fake_response):
        engine = PexelsEngine(api_key="fake-key")
        with pytest.raises(MaterialSearchError) as exc_info:
            engine.search_video(
                search_term="cat",
                minimum_duration=5,
                video_aspect=VideoAspect.portrait,
            )

    assert exc_info.value.search_term == "cat"
    assert exc_info.value.service == "pexels"


def test_pexels_engine_search_video_raises_on_request_exception():
    import requests

    from funmaterial.exceptions import MaterialSearchError
    from funmaterial.video.download import PexelsEngine
    from funmaterial.video.schema import VideoAspect

    with patch(
        "funmaterial.video.download.requests.get",
        side_effect=requests.ConnectionError("network down"),
    ):
        engine = PexelsEngine(api_key="fake-key")
        with pytest.raises(MaterialSearchError) as exc_info:
            engine.search_video(
                search_term="cat",
                minimum_duration=5,
                video_aspect=VideoAspect.portrait,
            )

    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, requests.ConnectionError)


def test_pixabay_engine_search_video_mocked():
    from funmaterial.video.download import PixabayEngine
    from funmaterial.video.schema import VideoAspect

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "hits": [
            {
                "duration": 15,
                "videos": {
                    "large": {
                        "width": 1080,
                        "height": 1920,
                        "url": "http://x/pixabay-v.mp4",
                        "size": 1234,
                        "thumbnail": "http://x/thumb.jpg",
                    }
                },
                "views": 1,
                "downloads": 2,
                "likes": 3,
                "comments": 0,
                "user_id": 42,
                "user": "someone",
                "tags": "cat, animal",
            }
        ]
    }

    with patch("funmaterial.api.pixabay.get", return_value=fake_response) as mock_get:
        engine = PixabayEngine(api_key="fake-key")
        items = engine.search_video(
            search_term="cat",
            minimum_duration=5,
            video_aspect=VideoAspect.portrait,
        )

    mock_get.assert_called_once()
    assert len(items) == 1
    assert items[0].url == "http://x/pixabay-v.mp4"


def test_pixabay_engine_search_video_raises_on_http_error():
    from funmaterial.exceptions import MaterialSearchError
    from funmaterial.video.download import PixabayEngine
    from funmaterial.video.schema import VideoAspect

    fake_response = MagicMock()
    fake_response.status_code = 403
    fake_response.text = "Forbidden"
    fake_response.url = "http://pixabay.example/api/videos/?q=cat"

    with patch("funmaterial.api.pixabay.get", return_value=fake_response):
        engine = PixabayEngine(api_key="fake-key")
        with pytest.raises(MaterialSearchError) as exc_info:
            engine.search_video(
                search_term="cat",
                minimum_duration=5,
                video_aspect=VideoAspect.portrait,
            )

    assert exc_info.value.search_term == "cat"
    assert exc_info.value.service == "pixabay"
    assert isinstance(exc_info.value.__cause__, Exception)


def test_pixabay_engine_search_video_does_not_mask_programming_errors():
    """非请求类异常（如代码缺陷）不应被伪装成 MaterialSearchError。"""
    from funmaterial.video.download import PixabayEngine
    from funmaterial.video.schema import VideoAspect

    with patch(
        "funmaterial.api.pixabay.get",
        side_effect=TypeError("unexpected programming error"),
    ):
        engine = PixabayEngine(api_key="fake-key")
        with pytest.raises(TypeError):
            engine.search_video(
                search_term="cat",
                minimum_duration=5,
                video_aspect=VideoAspect.portrait,
            )


def test_download_videos_unknown_source_returns_none():
    from funmaterial.video.download import download_videos

    result = download_videos(api_key="fake", search_terms=["cat"], source="unknown")
    assert result is None


def test_download_videos_pexels_source_uses_mocked_engine():
    from funmaterial.video import download as download_module

    fake_response = MagicMock()
    fake_response.json.return_value = {
        "videos": [
            {
                "duration": 20,
                "video_files": [
                    {"width": 1080, "height": 1920, "link": "http://x/v.mp4"}
                ],
            }
        ]
    }

    with (
        patch("funmaterial.video.download.requests.get", return_value=fake_response),
        patch(
            "funmaterial.video.download.save_video", return_value="/tmp/vid-fake.mp4"
        ),
    ):
        result = download_module.download_videos(
            api_key="fake-key",
            search_terms=["cat"],
            source="pexels",
            material_directory="/tmp/funmaterial_test_material",
            audio_duration=1.0,
        )

    assert result == ["/tmp/vid-fake.mp4"]


def test_download_videos_skips_failing_search_term_and_continues():
    """验证单个搜索词失败时不会中止整个批处理。"""
    from funmaterial.video import download as download_module

    fake_response = MagicMock()
    fake_response.json.return_value = {
        "videos": [
            {
                "duration": 20,
                "video_files": [
                    {"width": 1080, "height": 1920, "link": "http://x/v.mp4"}
                ],
            }
        ]
    }

    call_count = {"n": 0}

    def fake_get(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            bad = MagicMock()
            bad.json.return_value = {"error": "bad request"}
            return bad
        return fake_response

    with (
        patch("funmaterial.video.download.requests.get", side_effect=fake_get),
        patch(
            "funmaterial.video.download.save_video", return_value="/tmp/vid-fake.mp4"
        ),
    ):
        result = download_module.download_videos(
            api_key="fake-key",
            search_terms=["bad-term", "cat"],
            source="pexels",
            material_directory="/tmp/funmaterial_test_material",
            audio_duration=1.0,
        )

    assert result == ["/tmp/vid-fake.mp4"]


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def test_no_cli_entry_point_declared():
    """funmaterial 未声明 [project.scripts] 入口。

    本测试显式记录这一事实；后续新增 CLI 时，测试失败会提醒同步更新。
    """
    import tomllib
    from pathlib import Path

    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text())
    assert "scripts" not in data.get("project", {})
