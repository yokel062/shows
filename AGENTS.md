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
- 《亿万》第二季使用 `s02eXX/content.json`，运行 `python tools/build_billions.py --season 2 --complete`；模板为 `shared/season-two-episode.html`。第二季以查克、阿克斯、温迪三人为关系图核心，泰勒按本集行动加入外围人物；三条阶段关系依次为查克—阿克斯、查克—温迪、阿克斯—温迪。目录位于 `season-2/`，各篇只使用截至对应集已揭示的信息。
- 《亿万》第三季使用 `s03eXX/content.json`，运行 `python tools/build_billions.py --season 3 --complete`；模板为 `shared/season-three-episode.html`。前三季目录位于 `season-1/`、`season-2/`、`season-3/`，作品入口按季度展示。第三季关系图包含查克、阿克斯、温迪、泰勒四个核心人物，阶段说明中的五条关系依次为查克—阿克斯、查克—温迪、阿克斯—温迪、阿克斯—泰勒、温迪—泰勒。
- 场景的“这一场为什么重要 · 个人解读”默认展开。人物关系图使用 `shared/portraits.json` 注册的统一剧中角色照，同一人跨集复用，新增人物时补齐演员和图像出处。
- 《继承之战》第一季十集使用 `series/succession/s01eXX/content.json`，运行 `python tools/build_succession.py --complete`；只重建一集可用 `--episode 6`。首集保留独立模板 `shared/episode.html`，第 2—10 集使用 `shared/season-episode.html`；统一角色照登记在 `shared/portraits.json`。构建同时生成十集目录与 `season.json`，逐集限制剧透，不用后集事实解释前集选择。
- 《风骚律师》第一季十集使用 `series/better-call-saul/s01eXX/content.json`，修改后运行 `python tools/build_better_call_saul.py --complete`；单集可用 `--episode 6`。首集保留 `shared/episode.html`，第 2—10 集使用 `shared/season-episode.html`，共用 CSS、JS 与 `shared/portraits.json`。第六集以迈克为关系图中心，其余集以吉米为中心；每篇只用截至当集的信息，角色照不得取自后集。构建同时更新十集目录与 `season.json`。
- 整季目录默认显示全部集数的配图与导读，不按观看进度隐藏；单集入口在新标签页打开。

## Git 与发布

- 整个仓库根目录统一管理 Git，不在作品或单集目录中创建嵌套仓库。
- 代码托管在 `yokel062/shows`，网站通过 GitHub Pages 发布。
- 发布源为 `main` 分支的根目录；保留 `.nojekyll`。
- 用户已经指定 GitHub 为后续发布平台，不使用 ChatGPT Sites 或其他托管平台，除非用户另有明确要求。
- 提交前检查本地链接和资源、相关 JS 语法及 `git diff --check`。推送后确认远端 SHA，并等待 Pages 构建结果。
- 临时文件放 `/data/wangxw/tmp`，不要提交浏览器截图、缓存、凭证或平台专属本地元数据。
