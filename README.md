# funmaterial

素材获取工具库：从 Zenodo 归档、Pexels/Pixabay/Unsplash 等平台获取视频、背景音乐、字体等素材，主要用于短视频/内容生成类项目按关键词拉取背景视频、随机取一首背景音乐或字体。

## 安装

```bash
pip install funmaterial
```

## 用法示例

### 随机获取背景音乐 / 字体（来自 Zenodo 归档）

```python
from funmaterial.song import random_song_from_zenodo
from funmaterial.font import random_font_from_zenodo

song_path = random_song_from_zenodo()  # 默认 record_id=14286359，随机下载一首歌到 material/song/
font_path = random_font_from_zenodo()  # 默认 record_id=14286964，随机下载一个字体到 material/font/
```

### 按关键词搜索并下载视频素材（Pexels / Pixabay）

```python
from funmaterial.video.download import download_videos
from funmaterial.video.schema import VideoAspect, VideoConcatMode

video_paths = download_videos(
    api_key="your-pexels-or-pixabay-key",
    search_terms=["city night", "rain"],
    source="pexels",  # 或 "pixabay"
    material_directory="./material/video",
    video_aspect=VideoAspect.portrait,
    video_contact_mode=VideoConcatMode.random,
    audio_duration=30.0,
)
```

下载后会用 `moviepy` 校验视频文件是否有效（能打开、时长/帧率正常），无效文件会被自动删除。

### 调用图片 API（Pixabay / Unsplash）

```python
from funmaterial.api.pixabay import PixabayAPI
from funmaterial.api.unsplash import Unsplash

# api_key 未传时，会通过 funsecret 读取 "funmaterial"/"pixabay"/"api_key"
images = PixabayAPI(api_key="your-key").search_image(q="cat")

# access_key/secret_key 未传时，会通过 funsecret 读取 "funmaterial"/"unsplash"/"access_key" 和 "secret_key"
photos = Unsplash().search_photos(query="mountain")
```

## 说明

- `funmaterial.audio` 和 `funmaterial.picture` 两个子模块目前只有空的 `__init__.py`，尚未实现具体功能。
- 未提供命令行入口（`pyproject.toml` 中没有 `[project.scripts]`），只能作为 Python 库导入使用。
