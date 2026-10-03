from __future__ import annotations

from typing import Any

import requests
from funsecret import read_secret

from funmaterial.exceptions import MaterialAPIError


class Unsplash:
    """Unsplash 图片搜索客户端。

    接口文档：https://unsplash.com/documentation#search-users
    """

    def __init__(
        self, access_key: str | None = None, secret_key: str | None = None
    ) -> None:
        """初始化 Unsplash API 客户端。

        Args:
            access_key: Unsplash access key。未传时通过 `funsecret` 读取
                `"funmaterial"/"unsplash"/"access_key"`。
            secret_key: Unsplash secret key。未传时通过 `funsecret` 读取
                `"funmaterial"/"unsplash"/"secret_key"`。
        """
        self.access_key = access_key or read_secret(
            "funmaterial", "unsplash", "access_key"
        )
        self.secret_key = secret_key or read_secret(
            "funmaterial", "unsplash", "secret_key"
        )
        self.base_url = "https://api.unsplash.com/"

    def _get(self, uri: str, params: dict[str, Any]) -> Any:
        """向 Unsplash API 发起 GET 请求并返回解析后的 JSON。

        Args:
            uri: 相对 `base_url` 的接口路径。
            params: 查询参数。

        Returns:
            响应体解析后的 JSON 数据。

        Raises:
            MaterialAPIError: 网络异常、非 200 状态码或响应不是合法 JSON 时抛出，
                携带 service、url、status_code 上下文。
        """
        params["client_id"] = self.access_key
        url = f"{self.base_url}/{uri}"
        try:
            resp = requests.get(url, params=params, timeout=(30, 60))
        except requests.RequestException as e:
            raise MaterialAPIError(
                "Unsplash 请求异常", service="unsplash", url=url
            ) from e

        if resp.status_code != 200:
            raise MaterialAPIError(
                f"Unsplash 请求失败: {resp.text}",
                service="unsplash",
                url=resp.url,
                status_code=resp.status_code,
            )

        try:
            return resp.json()
        except ValueError as e:
            raise MaterialAPIError(
                "Unsplash 响应不是合法 JSON",
                service="unsplash",
                url=resp.url,
                status_code=resp.status_code,
            ) from e

    def list_photos(self, page: int = 1, per_page: int = 10) -> Any:
        """获取图片列表。

        Args:
            page: 页码，默认 1。
            per_page: 每页数量，默认 10。

        Returns:
            图片列表数据。
        """
        payload = {
            "page": page,
            "per_page": per_page,
        }
        return self._get("photos", payload)

    def get_photo(self, photo_id: str) -> Any:
        """获取单张图片详情。

        Args:
            photo_id: 图片 ID，必填。

        Returns:
            图片详情数据。
        """
        payload: dict[str, Any] = {}
        return self._get(f"photos/{photo_id}", payload)

    def get_photo_random(
        self,
        collections: str | None = None,
        topics: str | None = None,
        username: str | None = None,
        query: str | None = None,
        orientation: str | None = None,
        content_filter: str = "low",
        count: int = 1,
    ) -> Any:
        """随机获取图片。

        Args:
            collections: 用于筛选的公开合集 ID，多个用逗号分隔。
            topics: 用于筛选的公开话题 ID，多个用逗号分隔。
            username: 限定为某个用户的图片。
            query: 限定匹配某个搜索词的图片。
            orientation: 图片方向过滤，取值 landscape / portrait / squarish。
            content_filter: 内容安全等级，取值 low / high，默认 low。
            count: 返回图片数量，默认 1，最大 30。

        Returns:
            随机图片数据。
        """
        payload = {
            "collections": collections,
            "topics": topics,
            "username": username,
            "query": query,
            "orientation": orientation,
            "content_filter": content_filter,
            "count": count,
        }
        return self._get("photos/random", payload)

    def search_photos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "relevant",
        collections: str = "",
        content_filter: str = "low",
        color: str = "",
        orientation: str = "",
    ) -> Any:
        """搜索图片。

        Args:
            query: 搜索关键词。
            page: 页码，默认 1。
            per_page: 每页数量，默认 10。
            order_by: 排序方式，取值 latest / relevant，默认 relevant。
            collections: 用于缩小范围的合集 ID，多个用逗号分隔。
            content_filter: 内容安全等级，取值 low / high，默认 low。
            color: 颜色过滤，如 black_and_white、red、blue 等。
            orientation: 图片方向过滤，取值 landscape / portrait / squarish。

        Returns:
            图片搜索结果。
        """
        payload = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "order_by": order_by,
            "collections": collections,
            "content_filter": content_filter,
            "color": color,
            "orientation": orientation,
        }
        return self._get("search/photos", params=payload)

    def search_collection(self, query: str, page: int = 1, per_page: int = 10) -> Any:
        """搜索合集。

        Args:
            query: 搜索关键词。
            page: 页码，默认 1。
            per_page: 每页数量，默认 10。

        Returns:
            合集搜索结果。
        """
        payload = {
            "query": query,
            "per_page": per_page,
            "page": page,
        }
        return self._get("search/collections", params=payload)

    def search_users(self, query: str, page: int = 1, per_page: int = 10) -> Any:
        """搜索用户。

        Args:
            query: 搜索关键词。
            page: 页码，默认 1。
            per_page: 每页数量，默认 10。

        Returns:
            用户搜索结果。
        """
        payload = {
            "query": query,
            "per_page": per_page,
            "page": page,
        }
        return self._get("search/users", params=payload)

    def list_topic(
        self,
        ids: str | None = None,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "position",
    ) -> Any:
        """获取话题列表。

        Args:
            ids: 限定匹配的话题 ID 或 slug，多个用逗号分隔。
            page: 页码，默认 1。
            per_page: 每页数量，默认 10。
            order_by: 排序方式，取值 featured / latest / oldest / position。

        Returns:
            话题列表数据。
        """
        payload = {
            "ids": ids,
            "page": page,
            "per_page": per_page,
            "order_by": order_by,
        }
        return self._get("topics", params=payload)

    def topic_detail(self, id: str | None = None, slug: str | None = None) -> Any:
        """获取话题详情。

        Args:
            id: 话题 ID，与 `slug` 二选一必填。
            slug: 话题 slug，与 `id` 二选一必填。

        Returns:
            话题详情数据。
        """
        payload: dict[str, Any] = {}
        return self._get(f"topics/{id or slug}", params=payload)

    def topic_photos(
        self,
        id: str | None = None,
        slug: str | None = None,
        page: int = 1,
        per_page: int = 10,
        orientation: str | None = None,
        order_by: str = "latest",
    ) -> Any:
        """获取话题下的图片列表。

        Args:
            id: 话题 ID，与 `slug` 二选一必填。
            slug: 话题 slug，与 `id` 二选一必填。
            page: 页码，默认 1。
            per_page: 每页数量，默认 10。
            orientation: 图片方向过滤，取值 landscape / portrait / squarish。
            order_by: 排序方式，取值 latest / oldest / popular，默认 latest。

        Returns:
            话题下的图片列表。
        """
        payload = {
            "page": page,
            "per_page": per_page,
            "orientation": orientation,
            "order_by": order_by,
        }
        return self._get(f"topics/{id or slug}/photos", params=payload)

    def stats_total(self) -> Any:
        """获取 Unsplash 平台总量统计数据。

        Returns:
            总量统计数据。
        """
        return self._get("stats/total", params={})

    def stats_month(self) -> Any:
        """获取 Unsplash 平台月度统计数据。

        Returns:
            月度统计数据。
        """
        return self._get("stats/month", params={})
