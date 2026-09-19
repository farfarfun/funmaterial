# CHANGELOG

本文件记录 `funmaterial` 的版本变更，格式遵循「新增 / 修复 / 变更 / 废弃」分类，按版本倒序排列。

## [未发布]

### 修复

- 日志统一改用组织自有包 `farlog`（此前 `font/zenodo.py`、`song/zenodo.py`、`video/download.py` 使用 `funutil`）。
- 移除 `video/download.py` 模块执行入口中的 `print`，改为 `farlog` 日志输出。
- 新增 `funmaterial.exceptions` 领域异常（`MaterialAPIError`、`MaterialSearchError`），替换视频 / 图片搜索失败时吞掉异常、静默返回空列表的做法；异常信息携带服务名、URL、搜索词、状态码等上下文。
- `PixabayAPI.search_image` / `search_video` 请求失败时抛出 `MaterialAPIError`（原先是仅含响应文本的裸 `ValueError`）。
- `MaterialEngine.search_video` 基类方法改为显式抛出 `NotImplementedError`，明确「必须由子类实现」的契约，不再把未实现行为（`pass` 返回 `None`）当作可测试的功能路径。
- `to_json` 序列化失败时不再静默返回 `None`：记录带上下文（对象类型）的警告日志，并返回 `repr(obj)` 兜底。
- 修复 8 个 Dependabot 依赖安全告警（`cryptography`、`orjson`）。
- 补齐 `pillow` 版本下限至 `11.3.0`（`moviepy<12.0` 约束下的最新可用版本）。

### 新增

- 补充 `tests/test_smoke.py` 测试覆盖：`save_video` 正常 / 下载失败 / 视频无效路径，`Unsplash` 全部公开方法，`to_json` 边界情况，新增的领域异常路径。
- README 末尾追加组织统一的「关于 farfarfun」区块。
- `pyproject.toml` 补充 `license = "MIT"`、`license-files`、`authors` 字段。
- CI workflow 补充 `timeout-minutes`；第三方 GitHub Action 钉死到 commit SHA。

### 变更

- `.gitignore` 补充 `*.db`、`.run/`、`logs/` 等生成物忽略规则，并将已提交的历史日志文件（`logs/*.log.gz`）移出版本管理。
- 移除仓库自带的 Gitee 同步 workflow，统一由组织级 `daily-action/sync-gitee.yml` 每日批量同步。

## [1.0.26] 及更早版本

早于本 CHANGELOG 建立之前的版本未做逐条记录，具体改动见 Git 提交历史。
