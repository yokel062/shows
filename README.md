# 剧中人 · Shows

美剧与电影的图文解析档案。结合真实画面、剧情时间线、人物关系、台词和主题分析，以桌面阅读为主要体验。

**[在线目录](https://yokel062.github.io/shows/)** · **[GitHub 仓库](https://github.com/yokel062/shows)**

## 现有内容

| 作品 | 内容 | 剧透范围 | 在线阅读 |
| --- | --- | --- | --- |
| 兄弟连 · Band of Brothers | S01E01 · Currahee | 仅第 1 集 | [图解笔记](https://yokel062.github.io/shows/series/band-of-brothers/s01e01/) |

## 目录约定

```text
index.html
series/
  band-of-brothers/
    s01e01/
      index.html
      style.css
      app.js
      assets/
movies/
  <movie-slug>/
```

`movies/` 是后续电影内容的目录约定，目前尚无电影页面。

页面使用相对链接；单集可独立打开。图片存储在各篇的 `assets/` 中，Google Fonts 为可选字体来源，无法连接时使用系统字体。

## 本地预览

在仓库根目录启动静态服务器：

```bash
TMPDIR=/data/wangxw/tmp TMP=/data/wangxw/tmp TEMP=/data/wangxw/tmp \
  python -m http.server 38723 --directory .
```

打开 `http://localhost:38723/`。无需安装依赖或运行构建。

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
