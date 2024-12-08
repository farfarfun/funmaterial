import random

from fundrive import ZenodoDrive
from funget import simple_download
from funutil import getLogger

logger = getLogger("funmaterial")
drive = ZenodoDrive()


def random_song_from_zenodo(record_id=14286359):
    files = drive.get_file_list(record_id=record_id)
    files = sorted(files, key=lambda f: f["path"])
    song_info = random.choice(files)

    logger.info(f"random song: {song_info['path']}: {song_info}")
    file_path = f"material/song/{song_info['path']}"
    simple_download(url=song_info["url"], filepath=file_path, prefix="download-song")
    return file_path
