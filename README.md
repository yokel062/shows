# 剧中人 · Shows

美剧与电影的图文解析档案。结合真实画面、剧情时间线、人物关系、台词和主题分析，以桌面阅读为主要体验。

**[在线目录](https://yokel062.github.io/shows/)** · **[GitHub 仓库](https://github.com/yokel062/shows)**

## 现有内容

| 作品 | 内容 | 剧透范围 | 在线阅读 |
| --- | --- | --- | --- |
| 兄弟连 · Band of Brothers | 完整十集 | 单集包含截至该集的剧情 | [十集目录](https://yokel062.github.io/shows/series/band-of-brothers/) |

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
tools/
  build_episodes.py
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

## 编辑单集

第 1 集保留最初的独立页面。第 2—10 集使用 `content.json` 保存经过核对的文字、人物关系和配图出处，由共享阅读组件展示。修改数据后，在仓库根目录运行：

```bash
python tools/build_episodes.py --complete
```

工具会检查来源、图片、人物关系和台词长度，再生成单集 HTML 和整季目录数据。生成的 HTML 提交到仓库，线上不依赖 Python 或构建过程，也无需通过 JavaScript 请求 JSON。

十集的场景解读默认展开，读者可以手动收起。人物关系图、人物档案和关系详情统一复用 `shared/portraits.json` 中的剧中角色照；注册表记录演员、来源、原图链接和脸部裁切位置。同一人物的不同称呼通过别名映射到同一张照片，第 1 集的人物照也由构建工具同步更新，原有正文保留。

整季目录默认展示十集的全部配图与导读，单集入口在新标签页打开。每篇仍标明截至该集的剧透范围。

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
