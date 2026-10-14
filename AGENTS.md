# Shows 项目规则

## 内容与呈现

- 本仓库是美剧和电影图文解析的共同入口；按作品和集数组织内容。
- 以桌面浏览为主要使用方式，优先考虑宽幅剧照、并排对照、可读的文字和人物关系图；不安排专门的手机适配工作，除非用户要求。
- 对话、文档和内容分析使用简体中文；代码、标识符和代码注释使用英文。
- 每篇明确剧透边界；剧情事实、历史事实与个人解读分别标注。
- 台词核对原文，中文自译需说明。图片注明来源；配图和具体场景截图要区分。

## 目录

- `index.html`：所有作品的目录首页。
- `series/<show-slug>/sXXeYY/`：单集页面及其资源。
- `movies/<movie-slug>/`：电影页面及其资源。
- 优先使用无构建步骤的 HTML/CSS/JS，以及相对资源链接。
- 新增内容时同时更新首页和 README 中的目录。
- 《兄弟连》第 2—10 集的编辑源为各目录的 `content.json`；修改后运行 `python tools/build_episodes.py --complete` 生成静态 HTML 与整季目录数据。共享组件在 `series/band-of-brothers/shared/`。
- 第 1 集保留原独立页面；更改共享视觉时不要覆盖它的原内容。
- 《亿万》第一季十二集的编辑源为各目录的 `content.json`；修改后运行 `python tools/build_billions.py --complete`。默认生成第 2—12 集与整季目录，保留已确认的首集页面；修改首集后用 `--pilot --complete` 显式重建。第 2—12 集模板为 `series/billions/shared/season-episode.html`，首集模板为 `episode.html`。
- 场景的“这一场为什么重要 · 个人解读”默认展开。人物关系图使用 `shared/portraits.json` 注册的统一剧中角色照，同一人跨集复用，新增人物时补齐演员和图像出处。
- 整季目录默认显示全部集数的配图与导读，不按观看进度隐藏；单集入口在新标签页打开。

## Git 与发布

- 整个仓库根目录统一管理 Git，不在作品或单集目录中创建嵌套仓库。
- 代码托管在 `yokel062/shows`，网站通过 GitHub Pages 发布。
- 发布源为 `main` 分支的根目录；保留 `.nojekyll`。
- 用户已经指定 GitHub 为后续发布平台，不使用 ChatGPT Sites 或其他托管平台，除非用户另有明确要求。
- 提交前检查本地链接和资源、相关 JS 语法及 `git diff --check`。推送后确认远端 SHA，并等待 Pages 构建结果。
- 临时文件放 `/data/wangxw/tmp`，不要提交浏览器截图、缓存、凭证或平台专属本地元数据。
