import random

from fundrive import ZenodoDrive
from funget import simple_download
from funutil import getLogger

logger = getLogger("funmaterial")
drive = ZenodoDrive()


def random_font_from_zenodo(record_id=14286964):
    files = drive.get_file_list(record_id=record_id)
    files = sorted(files, key=lambda f: f["path"])
    font_info = random.choice(files)

    logger.info(f"random font: {font_info['path']}: {font_info}")
    file_path = f"material/font/{font_info['path']}"
    simple_download(url=font_info["url"], filepath=file_path, prefix="download-font")
    return file_path
