from __future__ import annotations

from typing import Any

from funsecret import read_secret
from requests import RequestException, get

from funmaterial.exceptions import MaterialAPIError


class PixabayAPI:
    """Pixabay 图片 / 视频搜索客户端。"""

    def __init__(
        self, api_key: str | None = None, base_url: str = "https://pixabay.com/api/"
    ) -> None:
        """初始化 Pixabay API 客户端。

        Args:
            api_key: Pixabay API key。未传时通过 `funsecret` 读取
                `"funmaterial"/"pixabay"/"api_key"`。注册地址：
                https://pixabay.com/en/accounts/register/ 。
            base_url: Pixabay API 根地址。
        """
        self.api_key = api_key or read_secret("funmaterial", "pixabay", "api_key")
        self.base_url = base_url

    def search_image(
        self,
        q: str,
        lang: str = "en",
        id: str = "",
        response_group: str = "image_details",
        image_type: str = "all",
        orientation: str = "all",
        category: str = "",
        min_width: int = 0,
        min_height: int = 0,
        editors_choice: str = "false",
        safesearch: str = "false",
        order: str = "popular",
        page: int = 1,
        per_page: int = 20,
        callback: str = "",
        pretty: str = "false",
    ) -> dict[str, Any]:
        """搜索 Pixabay 图片。

        Args:
            q: 搜索关键词，不超过 100 字符，为空表示返回全部图片。
            lang: 搜索语言代码（如 en、zh 等）。
            id: 指定图片 ID / hash ID，多个用逗号分隔。
            response_group: "image_details" 或 "high_resolution"（需权限）。
            image_type: "all" / "photo" / "illustration" / "vector"。
            orientation: "all" / "horizontal" / "vertical"。
            category: 分类过滤，如 nature、animals 等。
            min_width: 最小宽度（像素）。
            min_height: 最小高度（像素）。
            editors_choice: 是否仅返回编辑精选，"true" / "false"。
            safesearch: 是否仅返回全年龄向内容，"true" / "false"。
            order: 排序方式，"popular" 或 "latest"。
            page: 页码。
            per_page: 每页结果数，取值 3-200。
            callback: JSONP 回调函数名。
            pretty: 是否缩进输出 JSON，生产环境不建议开启。

        Returns:
            Pixabay 返回的图片搜索结果（已解析的 JSON）。

        Raises:
            MaterialAPIError: 网络异常、非 200 状态码或响应不是合法 JSON 时抛出，
                携带 URL 与状态码上下文。
        """
        payload = {
            "key": self.api_key,
            "q": q,
            "lang": lang,
            "id": id,
            "response_group": response_group,
            "image_type": image_type,
            "orientation": orientation,
            "category": category,
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": editors_choice,
            "safesearch": safesearch,
            "order": order,
            "page": page,
            "per_page": per_page,
            "callback": callback,
            "pretty": pretty,
        }

        try:
            resp = get(self.base_url, params=payload, timeout=(30, 60))
        except RequestException as e:
            raise MaterialAPIError(
                "Pixabay 图片搜索请求异常", service="pixabay", url=self.base_url
            ) from e
        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError as e:
                raise MaterialAPIError(
                    "Pixabay 图片搜索响应不是合法 JSON",
                    service="pixabay",
                    url=resp.url,
                    status_code=resp.status_code,
                ) from e
        raise MaterialAPIError(
            f"Pixabay 图片搜索请求失败: {resp.text}",
            service="pixabay",
            url=resp.url,
            status_code=resp.status_code,
        )

    def search_video(
        self,
        q: str,
        lang: str = "en",
        id: str = "",
        video_type: str = "all",
        category: str = "",
        min_width: int = 0,
        min_height: int = 0,
        editors_choice: str = "false",
        safesearch: str = "false",
        order: str = "popular",
        page: int = 1,
        per_page: int = 20,
        callback: str = "",
        pretty: str = "false",
    ) -> dict[str, Any]:
        """搜索 Pixabay 视频。

        Args:
            q: 搜索关键词，不超过 100 字符，为空表示返回全部视频。
            lang: 搜索语言代码（如 en、zh 等）。
            id: 指定视频 ID / hash ID，多个用逗号分隔。
            video_type: "all" / "film" / "animation"。
            category: 分类过滤，如 nature、animals 等。
            min_width: 最小宽度（像素）。
            min_height: 最小高度（像素）。
            editors_choice: 是否仅返回编辑精选，"true" / "false"。
            safesearch: 是否仅返回全年龄向内容，"true" / "false"。
            order: 排序方式，"popular" 或 "latest"。
            page: 页码。
            per_page: 每页结果数，取值 3-200。
            callback: JSONP 回调函数名。
            pretty: 是否缩进输出 JSON，生产环境不建议开启。

        Returns:
            Pixabay 返回的视频搜索结果（已解析的 JSON）。

        Raises:
            MaterialAPIError: 网络异常、非 200 状态码或响应不是合法 JSON 时抛出，
                携带 URL 与状态码上下文。
        """
        payload = {
            "key": self.api_key,
            "q": q,
            "lang": lang,
            "id": id,
            "video_type": video_type,
            "category": category,
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": editors_choice,
            "safesearch": safesearch,
            "order": order,
            "page": page,
            "per_page": per_page,
            "callback": callback,
            "pretty": pretty,
        }

        url = self.base_url + "videos/"
        try:
            resp = get(url, params=payload, timeout=(30, 60))
        except RequestException as e:
            raise MaterialAPIError(
                "Pixabay 视频搜索请求异常", service="pixabay", url=url
            ) from e
        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError as e:
                raise MaterialAPIError(
                    "Pixabay 视频搜索响应不是合法 JSON",
                    service="pixabay",
                    url=resp.url,
                    status_code=resp.status_code,
                ) from e
        raise MaterialAPIError(
            f"Pixabay 视频搜索请求失败: {resp.text}",
            service="pixabay",
            url=resp.url,
            status_code=resp.status_code,
        )
