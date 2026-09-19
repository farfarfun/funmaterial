from __future__ import annotations

import random

from farlog import getLogger
from fundrive.drives import ZenodoDrive
from funget import simple_download

logger = getLogger("funmaterial")
drive = ZenodoDrive()


def random_song_from_zenodo(record_id: int = 14286359) -> str:
    """从 Zenodo 素材库中随机下载一首背景音乐文件。

    Args:
        record_id: Zenodo 记录 ID，默认为组织维护的音乐素材库记录。

    Returns:
        下载后本地音乐文件的路径（`material/song/<文件名>`）。
    """
    files = drive.get_file_list(record_id=record_id)
    files = sorted(files, key=lambda f: f["path"])
    song_info = random.choice(files)

    logger.info(f"random song: {song_info['path']}: {song_info}")
    file_path = f"material/song/{song_info['path']}"
    simple_download(url=song_info["url"], filepath=file_path, prefix="download-song")
    return file_path
