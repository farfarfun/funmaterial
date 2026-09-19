from __future__ import annotations

import random

from farlog import getLogger
from fundrive.drives import ZenodoDrive
from funget import simple_download

logger = getLogger("funmaterial")
drive = ZenodoDrive()


def random_font_from_zenodo(record_id: int = 14286964) -> str:
    """从 Zenodo 素材库中随机下载一个字体文件。

    Args:
        record_id: Zenodo 记录 ID，默认为组织维护的字体素材库记录。

    Returns:
        下载后本地字体文件的路径（`material/font/<文件名>`）。
    """
    files = drive.get_file_list(record_id=record_id)
    files = sorted(files, key=lambda f: f["path"])
    font_info = random.choice(files)

    logger.info(f"random font: {font_info['path']}: {font_info}")
    file_path = f"material/font/{font_info['path']}"
    simple_download(url=font_info["url"], filepath=file_path, prefix="download-font")
    return file_path
