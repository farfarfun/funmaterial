"""funmaterial 领域异常。

素材搜索、下载相关的失败统一抛出这里定义的异常类型，而不是裸
``Exception``/``ValueError``，并在异常信息里带上服务名、URL、搜索词、
状态码等上下文，方便定位问题。
"""

from __future__ import annotations


class FunMaterialError(Exception):
    """funmaterial 所有领域异常的基类。"""


class MaterialAPIError(FunMaterialError):
    """第三方素材 API（Pixabay / Unsplash 等）请求失败。

    Args:
        message: 失败的简要描述。
        service: 目标服务名，如 "pixabay"、"unsplash"。
        url: 请求的 URL（如可获得）。
        status_code: HTTP 状态码（如可获得）。
    """

    def __init__(
        self,
        message: str,
        *,
        service: str,
        url: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.service = service
        self.url = url
        self.status_code = status_code
        context = f"service={service}"
        if status_code is not None:
            context += f", status_code={status_code}"
        if url is not None:
            context += f", url={url}"
        super().__init__(f"{message} ({context})")


class MaterialSearchError(MaterialAPIError):
    """素材搜索失败，在 :class:`MaterialAPIError` 基础上附带搜索词。

    Args:
        message: 失败的简要描述。
        service: 目标服务名，如 "pexels"、"pixabay"。
        search_term: 触发失败的搜索词。
        url: 请求的 URL（如可获得）。
        status_code: HTTP 状态码（如可获得）。
    """

    def __init__(
        self,
        message: str,
        *,
        service: str,
        search_term: str,
        url: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.search_term = search_term
        super().__init__(
            f"{message}, search_term={search_term!r}",
            service=service,
            url=url,
            status_code=status_code,
        )
