# 剧中人 · Shows

美剧与电影的图文解析档案。结合真实画面、剧情时间线、人物关系、台词和主题分析，以桌面阅读为主要体验。

**[在线目录](https://yokel062.github.io/shows/)** · **[GitHub 仓库](https://github.com/yokel062/shows)**

## 现有内容

| 作品 | 内容 | 剧透范围 | 在线阅读 |
| --- | --- | --- | --- |
| 绝命毒师 · Breaking Bad | 第一季完整七集 | 单集包含截至该集的剧情，不涉及第二季 | [七集目录](https://yokel062.github.io/shows/series/breaking-bad/) |
| 兄弟连 · Band of Brothers | 完整十集 | 单集包含截至该集的剧情 | [十集目录](https://yokel062.github.io/shows/series/band-of-brothers/) |
| 亿万 · Billions | 第一至第三季，各十二集 | 单集包含截至该集的剧情 | [季度目录](https://yokel062.github.io/shows/series/billions/) |
| 白莲花 · The White Lotus | 第一季第一集 · Arrivals | 仅 S01E01，含本集结尾 | [首集图解](https://yokel062.github.io/shows/series/the-white-lotus/s01e01/) |
| 继承之战 · Succession | 第一季完整十集 | 单集包含截至该集的剧情，不涉及第二季 | [十集目录](https://yokel062.github.io/shows/series/succession/) |

## 兄弟连十集目录

| 集数 | 标题 | 在线阅读 |
| --- | --- | --- |
| 01 | Currahee | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e01/) |
| 02 | Day of Days | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e02/) |
| 03 | Carentan | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e03/) |
| 04 | Replacements | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e04/) |
| 05 | Crossroads | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e05/) |
| 06 | Bastogne | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e06/) |
| 07 | The Breaking Point | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e07/) |
| 08 | The Last Patrol | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e08/) |
| 09 | Why We Fight | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e09/) |
| 10 | Points | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e10/) |

## 亿万第一季十二集

**[第一季完整目录](https://yokel062.github.io/shows/series/billions/season-1/)**

每集以三幕组织剧情节点，配真实截图或明确标注的宣传剧照，包含分阶段人物关系、消息与选择路径、对照深读和英文短台词卡。剧情事实与个人解读分别标注，场景解读默认展开，图片出处逐张登记；每篇只讨论截至该集的内容。首集保留已完成的重做版本。

| 集数 | 标题 | 在线阅读 |
| --- | --- | --- |
| 01 | Pilot | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e01/) |
| 02 | Naming Rights | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e02/) |
| 03 | YumTime | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e03/) |
| 04 | Short Squeeze | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e04/) |
| 05 | The Good Life | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e05/) |
| 06 | The Deal | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e06/) |
| 07 | The Punch | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e07/) |
| 08 | Boasts and Rails | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e08/) |
| 09 | Where the F*ck Is Donnie? | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e09/) |
| 10 | Quality of Life | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e10/) |
| 11 | Magical Thinking | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e11/) |
| 12 | The Conversation | [图解笔记](https://yokel062.github.io/shows/series/billions/s01e12/) |

文字编辑源为 `series/billions/s01eXX/content.json`，统一角色照登记在 `series/billions/shared/portraits.json`。修改后运行：

```bash
python tools/build_billions.py --complete
```

工具核验十二集数据，生成第 2—12 集、第一季目录、作品目录与 `season.json`，默认保留首集 HTML。第 2—12 集模板为 `shared/season-episode.html`，共用 `episode.css`、`season.css` 和 `episode.js`。只生成一集可使用 `--episode 5`；修改首集正文后使用 `python tools/build_billions.py --pilot --complete`，由保留的首集模板与构建器重新生成。生成后的 HTML 提交到仓库，网站无需线上构建。

## 亿万第二季十二集

**[第二季完整目录](https://yokel062.github.io/shows/series/billions/season-2/)** · **[全部已收录季度](https://yokel062.github.io/shows/series/billions/)**

十二集以三幕呈现剧情因果、真实配图、人物关系、消息路径、对照深读与短台词。关系图以查克、阿克斯、温迪为核心，并按当集行动纳入泰勒等人物。每篇限定到本集结尾，特别区分倒叙、人物掌握的信息与观众此刻所知，保留第二季后段的揭示顺序。

| 集数 | 标题 | 在线阅读 |
| --- | --- | --- |
| 01 | Risk Management | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e01/) |
| 02 | Dead Cat Bounce | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e02/) |
| 03 | Optimal Play | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e03/) |
| 04 | The Oath | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e04/) |
| 05 | Currency | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e05/) |
| 06 | Indian Four | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e06/) |
| 07 | Victory Lap | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e07/) |
| 08 | The Kingmaker | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e08/) |
| 09 | Sic Transit Imperium | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e09/) |
| 10 | With or Without You | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e10/) |
| 11 | Golden Frog Time | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e11/) |
| 12 | Ball in Hand | [图解笔记](https://yokel062.github.io/shows/series/billions/s02e12/) |

编辑源为 `series/billions/s02eXX/content.json`，共享人物照复用 `shared/portraits.json`。修改后运行：

```bash
python tools/build_billions.py --season 2 --complete
python tools/validate_site.py
```

单集模板为 `shared/season-two-episode.html`；仅生成一篇可用 `--season 2 --episode 5`。整季构建同时更新三个季度的目录导航，不重写其他季度的单集正文。

## 亿万第三季十二集

**[第三季完整目录](https://yokel062.github.io/shows/series/billions/season-3/)** · **[全部已收录季度](https://yokel062.github.io/shows/series/billions/)**

沿用三幕剧情、真实配图、消息路径、对照深读与台词笔记，人物关系扩展为查克、阿克斯、温迪和泰勒四个核心位置，按本集的三个阶段切换。剧情事实与个人解读分开，图像注明场景范围和出处；各篇包含必要的前季背景，只剧透到第三季对应集，不引入后季解释。

| 集数 | 标题 | 在线阅读 |
| --- | --- | --- |
| 01 | Tie Goes to the Runner | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e01/) |
| 02 | The Wrong Maria Gonzalez | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e02/) |
| 03 | A Generation Too Late | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e03/) |
| 04 | Hell of a Ride | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e04/) |
| 05 | Flaw in the Death Star | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e05/) |
| 06 | The Third Ortolan | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e06/) |
| 07 | Not You, Mr. Dake | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e07/) |
| 08 | All the Wilburys | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e08/) |
| 09 | Icebreaker | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e09/) |
| 10 | Redemption | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e10/) |
| 11 | Kompenso | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e11/) |
| 12 | Elmsley Count | [图解笔记](https://yokel062.github.io/shows/series/billions/s03e12/) |

编辑源为 `series/billions/s03eXX/content.json`，共享人物照继续登记在 `shared/portraits.json`。修改后运行：

```bash
python tools/build_billions.py --season 3 --complete
python tools/validate_site.py
```

只渲染一篇可使用 `--season 3 --episode 5`。第三季模板为 `shared/season-three-episode.html`，在既有组件上增加 `season-three.css` 的四人关系布局。季度目录分别为 `season-1/`、`season-2/` 与 `season-3/`，作品入口展示已收录季度。线上使用预先生成的静态 HTML，无需构建或运行时拉取 JSON。

## 白莲花首集档案

**[作品目录](https://yokel062.github.io/shows/series/the-white-lotus/)** · **[S01E01 · Arrivals](https://yokel062.github.io/shows/series/the-white-lotus/s01e01/)**

暖白与深绿的桌面阅读页面，以三幕、十个剧情节点梳理抵达的第一天；十一位人物复用统一角色照，五组冲突关系可切换查看。另有三组画面对照、三句英文短台词及本集结尾的已知／未知边界。场景解读默认展开，画面支持点击放大和 Escape 关闭。剧情事实、个人解读及图像对应范围分别标注，逐张原图和演员出处见篇末；仅讨论首集，不提前揭晓死亡事件。

文字和图片登记源为 `series/the-white-lotus/s01e01/content.json`，统一角色照登记在 `series/the-white-lotus/shared/portraits.json`。修改后运行：

```bash
python tools/build_white_lotus.py
```

单集与目录模板、CSS、JS 均在 `series/the-white-lotus/shared/`。构建后得到完整静态 HTML，无需线上构建，也不依赖运行时请求 JSON；关闭 JavaScript 仍可阅读所有剧情与冲突关系。

## 继承之战第一季十集档案

**[第一季十集目录](https://yokel062.github.io/shows/series/succession/)** · **[GitHub 内容目录](https://github.com/yokel062/shows/tree/main/series/succession)**

墨黑、象牙白与暗金的桌面阅读页面，从《Celebration》的生日交接写到《Nobody Is Ever Missing》的英国婚礼。保留首集完成的十二节点版本，第 2—10 集各有三幕、九个剧情节点；全季共 93 个节点、32 组人物冲突深读、105 张对应集数的真实剧照与 20 位人物的统一角色照。

每篇包含前情与开场、分阶段人物关系、关键机制的因果路径、英文短台词及三个画面呼应。剧情事实与个人解读分开，分析默认展开，图像逐张说明对应范围并登记原图。关系图不会把人物怀疑写成事实，也不把私下支持等同于已经投票；单集只使用截至该集已揭示的信息，不引入第二季解释。

整季目录以第一季家族宣传照为封面，按“权力空位—反抗父亲—重新回归”分组十集，采用深色页面与两列宽幅剧照，提供十集直达导航及三组人物冲突入口。目录选图、主题词、章节和冲突导读登记在 `shared/catalogue.json`；宣传照明确标注“非正片截图”及来源，各集卡片只用对应集的正片截图。样式和导航分别位于 `shared/catalogue.css`、`shared/catalogue.js`。全部配图与导读默认展示，单集在新标签页打开；各集有前后导航。关闭 JavaScript 仍可阅读全部人物、冲突和台词，图片可直接打开原始构图。英文短句均核对本集转录、注明中文自译，各篇引用总量限定在 25 个英文词内。

| 集数 | 原名 | 在线阅读 |
| --- | --- | --- |
| 01 | Celebration | [图文解读](https://yokel062.github.io/shows/series/succession/s01e01/) |
| 02 | Shit Show at the Fuck Factory | [图文解读](https://yokel062.github.io/shows/series/succession/s01e02/) |
| 03 | Lifeboats | [图文解读](https://yokel062.github.io/shows/series/succession/s01e03/) |
| 04 | Sad Sack Wasp Trap | [图文解读](https://yokel062.github.io/shows/series/succession/s01e04/) |
| 05 | I Went to Market | [图文解读](https://yokel062.github.io/shows/series/succession/s01e05/) |
| 06 | Which Side Are You On? | [图文解读](https://yokel062.github.io/shows/series/succession/s01e06/) |
| 07 | Austerlitz | [图文解读](https://yokel062.github.io/shows/series/succession/s01e07/) |
| 08 | Prague | [图文解读](https://yokel062.github.io/shows/series/succession/s01e08/) |
| 09 | Pre-Nuptial | [图文解读](https://yokel062.github.io/shows/series/succession/s01e09/) |
| 10 | Nobody Is Ever Missing | [图文解读](https://yokel062.github.io/shows/series/succession/s01e10/) |

编辑源为 `series/succession/s01eXX/content.json`，统一角色照登记在 `series/succession/shared/portraits.json`。修改后运行：

```bash
python tools/build_succession.py --complete
node --check series/succession/shared/episode.js
python tools/validate_site.py
```

只生成一篇可使用 `--episode 6`；首集模板为 `shared/episode.html`，第 2—10 集为 `shared/season-episode.html`，共享 `episode.css`、`episode.js`。构建同时生成作品目录和 `season.json`；`--complete` 要求十集齐备。生成后的 HTML 直接供 GitHub Pages 使用，无需线上构建或运行时拉取 JSON。

## 目录约定

```text
index.html
series/
  band-of-brothers/
    index.html
    shared/
    s01e01/
      index.html
      style.css
      app.js
      assets/
    s01e02/ ... s01e10/
      content.json
      index.html
      assets/
  billions/
    index.html
    season.json
    shared/
    s01e01/ ... s01e12/
      content.json
      index.html
      assets/
tools/
  build_episodes.py
  build_billions.py
  build_succession.py
movies/
  <movie-slug>/
```

`movies/` 是后续电影内容的目录约定，目前尚无电影页面。

页面使用相对链接；单集可独立打开。场景图片存储在各篇的 `assets/` 中，全季人物照存储在 `shared/portraits/`。Google Fonts 为可选字体来源，无法连接时使用系统字体。

## 本地预览

在仓库根目录启动静态服务器：

```bash
TMPDIR=/data/wangxw/tmp TMP=/data/wangxw/tmp TEMP=/data/wangxw/tmp \
  python -m http.server 38723 --directory .
```

打开 `http://localhost:38723/`。无需安装依赖或运行构建。

## 编辑兄弟连单集

第 1 集保留最初的独立页面。第 2—10 集使用 `content.json` 保存经过核对的文字、人物关系和配图出处，由共享阅读组件展示。修改数据后，在仓库根目录运行：

```bash
python tools/build_episodes.py --complete
```

工具会检查来源、图片、人物关系和台词长度，再生成单集 HTML 和整季目录数据。生成的 HTML 提交到仓库，线上不依赖 Python 或构建过程，也无需通过 JavaScript 请求 JSON。

十集的场景解读默认展开，读者可以手动收起。人物关系图、人物档案和关系详情统一复用 `shared/portraits.json` 中的剧中角色照；注册表记录演员、来源、原图链接和脸部裁切位置。同一人物的不同称呼通过别名映射到同一张照片，第 1 集的人物照也由构建工具同步更新，原有正文保留。

整季目录默认展示十集的全部配图与导读，单集入口在新标签页打开。每篇仍标明截至该集的剧透范围。

## 绝命毒师第一季七集档案

**[第一季七集目录](https://yokel062.github.io/shows/series/breaking-bad/)** · **[GitHub 内容目录](https://github.com/yokel062/shows/tree/main/series/breaking-bad)**

完整收录第一季七集：每集三幕、十二个剧情节点、三阶段人物关系、四组冲突、三段经核对的短对白与六处镜头细读，共 84 个节点与 28 组冲突。逐集限剧透，不用后续身份、人物命运或旧史替前集作判断。

编辑源为各集 `series/breaking-bad/s01eXX/content.json`。首集保留独立模板 `shared/episode.html`，第 2—7 集使用 `shared/season-episode.html`；样式、交互脚本及统一角色照登记也位于 `shared/`。修改后运行：

```bash
python tools/build_breaking_bad.py --complete
python tools/validate_site.py
node --check series/breaking-bad/shared/episode.js
```

只重建一集可用 `python tools/build_breaking_bad.py --episode 5`。构建同时更新七集目录与 `season.json`，验证逐集正文、来源、图像尺寸及短对白长度。图片区分对应场景截图、同集关联配图与本集宣传剧照；18 位人物使用统一的已登记角色照。

目录直接展示全部七集，入口在新标签页打开；单集包含前后集导航。无需 JavaScript 也可阅读全部正文、人物档案、阶段记录、冲突与台词。

## 后续发布

整个 `shows` 由一个 Git 仓库管理。GitHub Pages 从 `main` 分支的根目录发布，推送后自动更新：

```bash
git diff --check
git add <changed-files>
git commit -m "Add episode notes"
git push origin main
```

新增美剧页面放入 `series/<show-slug>/sXXeYY/`；新增电影放入 `movies/<movie-slug>/`。完成内容后更新首页的目录入口，并核对 Pages 构建与线上页面。

## 内容说明

剧情事实与个人解读分别标注；每篇限定剧透范围，参考资料链接可能包含更多剧情。台词只选用短句，中文翻译注明为自译。剧集画面版权属于原权利人，用于对应作品的阅读和评论；本仓库未授予这些画面的再分发许可。具体图片和文字来源见各篇末尾。
