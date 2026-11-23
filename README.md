# 纹谱 Wenpu

**世界纹样生成器。** 三百七十八种传统图案元素，按几何规则实时算出四方连续图案，直接导出成品。界面中英双语，菜单栏右侧一键切换。

> English version below — [jump to English](#wenpu).

### 在线直接用

**<https://podcatcher962.github.io/wenpu/>** —— 手机、平板、电脑都能开，不用装，不用登录。英文界面直接在地址后加 `?lang=en`。

在线版就是全部功能，因为它本来就是一个 HTML 文件。下面这几种只是「不想开浏览器」时的替代：

| 平台 | 包 | 说明 |
|---|---|---|
| Windows | `Wenpu.exe` | 免安装，双击即用，导出直接落到「图片\纹谱」 |
| 安卓 | `Wenpu.apk` | 独立应用，导出落到「下载/纹谱」，兼容 Android 5.0 以上 |
| Linux | `Wenpu-3.3-linux.tar.gz` | 源码 + 启动脚本；有 pywebview 开窗口，没有就用浏览器 |

三个包都在 [Releases](../../releases) 里。也可以直接双击 `index.html`——不用装、不用联网、不上传任何东西。

---

## 一句话说清它解决什么

网上的纹样素材有三个麻烦：要么是图片（放大就糊）、要么要注册会员、要么得自己拼成无缝的。

纹谱把纹样当成**规则**而不是图片：改格数、线宽、边距，整张图重排，边缘永远接得上。要矢量给 SVG，要打印给 PDF，要发朋友圈给 JPG。

---

## 三百七十八种图案元素，七组都过五十

不是贴图素材，每一个都是按几何规则算出来的。分七个地域，每个地域五十种以上，中国最多（64 种）。下表每组只列十二个代表，完整清单在软件里。

| 地域 | 数量 | 代表图案 |
|---|---|---|
| **中国** | 64 | 回纹 · 云雷纹 · 万字纹 · 方胜纹 · 毬路纹 · 八达晕 · 盘长纹 · 宝相花 · 缠枝纹 · 忍冬纹 · 海水江崖 · 山字纹 |
| **日本** | 54 | 青海波 · 麻叶纹 · 七宝纹 · 市松 · 纱绫形 · 鹿の子 · 亀甲 · 籠目 · 矢絣 · 小桜 · 梅鉢 · 高麗縁 |
| **西亚 · 中亚** | 52 | 八角星 · 佩斯利 · 郁金香 · 库法带 · 木格屏 · 米哈拉布拱 · 砖饰格 · 苏扎尼花 · 羊角纹 · 伊斯法罕章 · 六角星 · 圆章 |
| **欧洲** | 52 | 凯尔特结 · 希腊回纹 · 百合花饰 · 玫瑰窗 · 茛苕叶 · 大马士革 · 哥特窗花 · 鱼鳞板 · 挪威雪花 · 圆花饰 · 苏格兰格 · 蛋箭饰 |
| **非洲** | 52 | 泥布纹 · 肯特纹 · 埃塞十字 · 阿丁克拉折线 · 大王冠 · 锁链纹 · 合院纹 · 库巴拼贴 · 埃及莲纹 · 提非纳刻纹 · 马赛环带 · 恩德贝莱彩墙 |
| **美洲** | 52 | 印加阶梯 · 纳瓦霍菱 · 玛雅回纹 · 印加十字 · 希皮博 · 阿兹特克 · 马拉若阿拉 · 纳瓦霍风暴毯 · 玛雅阶梯 · 拉科塔晨星 · 印加太阳 · 亚马逊 Kené |
| **亚太** | 52 | 蜡染斜纹 · 银蕨螺旋 · 曼陀罗 · 卡翁 · 宋吉锦 · 毛利卷浪 · 巴厘波冷格 · 泰式卡诺 · 印度朗格丽 · 夏威夷拼布 · 东山螺旋 · 印度莲花 |

**每一种都在画布下方配一张科普卡**：形态怎么构成、从哪来、今天能用在什么地方。字号按正文排，不是脚注。每一条科普都有对应的英文，不是机翻。

---

## 中英双语

菜单栏右侧有一个小按钮，中文时写着 `EN`，英文时写着「中」，点一下整个界面换语言：

- **界面**：用途、地域、气质、配色、密度、做旧、接法、导出，全部换
- **内容**：378 条图案的名字、副标、科普正文、适用场景，全部换
- **文档**：使用说明、关于、开源、免责四篇，各有一份英文
- **记住选择**：下次打开还是上次的语言

地址栏参数可以指定：`?lang=en` 直接进英文版。

界面文案写在同一份 HTML 里，没有外部语言包——因为它要能离线单文件运行。中文文案带 `data-zh`/`data-en` 属性，图案文案在 `MENU` 表里按 id 对应。

---

## 能直接用的九种尺寸，加一个自定义

出来的不是「一张图案」，是**能发的图**和**能印的纸**。

| 用途 | 尺寸 | 拿去干什么 |
|---|---|---|
| 手机壁纸 | 1179×2556 | 直接设 |
| 小红书竖图 | 1080×1440 | 发笔记封面 |
| 小红书方图 | 1080×1080 | 发笔记 |
| 名片底纹 | 1050×600 | 90×51mm，印刷 |
| 书签 | 591×1772 | 50×150mm，打印后裁 |
| 纸胶带 | 2126×531 | 180×45mm 循环稿，可交给厂家 |
| A4 打印 | 2480×3508 | 包装纸、剪纸、描摹 |
| 电脑壁纸 | 2560×1440 | 2K |
| 平铺素材 | 1024×1024 | 网页、PPT 背景，强制无缝无边距 |
| **自定义** | 200–6000 px | 自己填宽高，另有 1:1 / 3:4 / 4:5 / 9:16 / 16:9 / A4 / 名片 七个快捷比例 |

### 做旧

一条强度滑块：泛黄、纸颗粒、水渍斑点、四角暗沉。拉到 40–60 最像旧纸。做旧是实时算的，不是套一张旧纸滤镜——每一版都跟着种子变。

PNG、JPG、WebP、PDF 都会带上；SVG 是矢量线稿，不做旧（界面上有写明）。

### 题字与落款

打字就出现，不用再勾选。可以在底部或顶部加一条衬纸签条，右下角落一枚「纹谱」朱印。

---

## 六种导出格式

| 格式 | 什么时候用 | 实测体积（1080×1440） |
|---|---|---|
| **PNG** | 发社交平台，线条最锐 | 810 KB |
| **JPG** | 要小一点，画质够用 | 515 KB |
| **WebP** | 网页用，最省 | 445 KB |
| **SVG** | 矢量，印刷厂和胶带厂要这个 | 468 KB（含 2560 条路径） |
| **PDF** | 按 300dpi 原尺寸打印，直接进打印机 | 一页，内嵌 JPEG |
| **透明 PNG** | 叠到自己的照片、PPT、海报上 | 同 PNG |

另有两个复制按钮：**平铺 CSS**（给做网页和公众号的）和**配色清单**（HEX + 线宽参数，给设计的）。

---

## 三个真实场景

**① 我要画一个** —— 开「图纸网格」，整张图叠上细网格，每五格一条深线，角上标出「每格 x mm · 共 N 格」。再开「淡显描摹」，纹样变淡，打印出来就能直接在上面描。刺绣、木工、剪纸、手账都按格数算。

**② 我要照着拍的东西做** —— 「从照片取色」。拍一张布、一块砖、一件旧木器，读它最重的几个颜色，点一下就成了纹色或底色。全程在本地读图，不上传。

**③ 我只想要个感觉** —— 五个气质预设：素雅、富丽、古拙、清冷、民俗。每个是一组配色 + 线宽 + 密度 + 接法的组合，点一下就换整个调子。

### 对花接法

- **左右对花** —— 相邻两列互为镜像，接缝处形成对称轴，像织物对花
- **四向对花** —— 上下左右都镜像，出来是万花筒式的对称

实现上是把「原贴图 + 它的镜像」拼成一个双倍大的超级贴图再平铺。接缝处的路径是同一个形状的镜像，数学上必然连续。

---

## 菜单栏

顶部四个入口，加一个语言按钮：

- **使用说明** —— 三步出图、几个好用的组合、地址栏参数
- **关于** —— 定位、收录范围、技术说明、作者
- **开源** —— MIT 许可能做什么、要保留什么
- **免责** —— 纹样的性质、数据怎么处理、印刷注意事项
- **`EN` / 「中」** —— 切换中英文界面

---

## 技术说明

- **单文件**，`index.html` 一个，约 463 KB（含中英两套文案），无依赖、无构建、无框架
- **一份几何，两个后端**：图案函数返回指令数组（M / L / Q / C / O），canvas 和 SVG 共用同一份路径数据，所以预览和导出必然一致
- **无缝原理**：贴图按 2×2 单元构造，画面四周各多铺一圈；对花模式把贴图与其镜像拼成 2 倍超级贴图
- **做旧用合成模式**：泛黄走 multiply、颗粒走 pattern、暗角走径向渐变，不逐像素扫，A4 也在 100 ms 量级
- **双语不重新加载**：切换语言时清空控件容器重建，状态（图案、配色、尺寸）留在内存与 localStorage 里，画面不闪
- 文件格式都是手写的：PDF 是一个约 60 行的最小写入器（一页 + 内嵌 JPEG + xref 表），没有引入 pdf 库

---

## 本版实测

- **378 个图案元素，七组各 52–64 种**，逐批截图目视检查
- **378 条英文文案全部人工翻译**，脚本核过：id 一一对应、无缺失、无多余、无中文残留（唯一例外是有意保留的品牌字「纹」与语言按钮「中」）
- 双语渲染用 headless Edge 的 DOM 快照核过：中文 378 个按钮、英文 378 个按钮，标题、科普卡、分组计数、状态栏逐项对得上
- 语言切换实测：点一次到英文，`uses` 仍是 10 个按钮（没有重复堆叠），画布说明变 `Phone wallpaper`；再点回中文，`lang` 回到 `zh-CN`
- 四篇文档双语核过：英文标题 `Guide`，正文首句 `Three steps to an image`；切回中文是「关于纹谱」
- 390px 宽度中英双版都无横向溢出；英文的长词（West & Central Asia、Desktop wallpaper）正常换行
- 体积从 321 KB 涨到 463 KB，涨的部分是 378 条英文科普（约 113 K 字符）与界面字典
- 修掉的问题都在截图里看出来：双线分支的指令索引错了一位，整页渲染中断、画布全白；尖拱的圆弧角度跨了整圈，拱形绕成一团乱线；密度参数给得过密，六角砖与蕾丝糊成一块实心红；尖瓣花的内腰太窄，画出来像五角星
- 九种尺寸满幅渲染 6–40 ms，A4 最慢
- SVG 经 DOMParser 校验通过：单排 2560 条路径 / 468 KB
- PDF 结构校验通过：`%PDF-1.4` 开头、`%%EOF` 结尾、xref 偏移正确、含 `/DCTDecode`
- 做旧强度 0 与 55 在同一张图上的像素方差差异明显，导出 PNG 可见

## 用法

**最省事**：开上面那个在线地址。

**离线**：双击 `index.html`。手机把文件传过去用浏览器打开也行。

**桌面版**：Windows 双击 `Wenpu.exe`。它不是「用浏览器套个壳」——程序里起一个只读的本地服务，
页面从 `http://127.0.0.1` 进来，所以是正经安全上下文；导出走本地通道，直接落盘到
`图片\纹谱`，不用去下载文件夹翻。

**安卓版**：装 `Wenpu.apk`。权限只有一条（网络，用于那个本地服务回环），不申请存储、相机、
麦克风。导出落到 `下载/纹谱/`。设置存在应用自己的 localStorage 里，关掉再开还在。

链接参数可以复现某个图案，方便分享：

```
index.html?m=baoxiang&u=xhs34&sym=p4&cells=8&lw=6&lang=en
```

`m` 图案 · `u` 用途 · `sym` 接法（p1/p2/p4）· `cells` 格数 · `lw` 线宽 · `lang` 界面语言（zh/en）。

---

## 边界

- 图案是**几何抽象**，不是考古复原图。它给出的是那个纹样的构成规则，不是某件文物的描摹。龙、凤、人物、器物这类具象题材没有收，因为几何生成器做不出它们的造型
- 英文名尽量取该纹样在英文文献里通行的叫法（meander、kufic、adinkra），没有通行名的用音译（tatewaku、elibelinde）；科普正文是给普通人读的，不是学术引用来源
- 「图纸网格」的毫米数按 300dpi 换算，实际打印请确认打印机没开「适应页面」
- SVG 里的文字用系统楷体，换到没装楷体的机器上会回退成宋体
- 纸胶带稿是循环单元，出血和专色要交给厂家处理

---

## 许可

MIT。可自由使用、修改、再发布，含商用。

**唯一要求是保留署名。** 源码里、`LICENSE` 里、以及任何改编版本的关于页或致谢页里，
这一行要留着：

```
Copyright (c) 2026 Lanlan Eternal
```

改名再发布不用问、不用付费、不用公开你的改动。加一句「基于纹谱」会让别人还能找回来，
那是礼貌，不是条件。详见 `NOTICE`。

---

# Wenpu

**A generator for the world's patterns.** 378 traditional pattern motifs, computed live from geometric rules into a seamless repeat, exported straight to a finished file. Chinese and English interface, switched from the button at the right of the menu bar.

### Use it online

**<https://podcatcher962.github.io/wenpu/>** — works on phone, tablet and desktop. Nothing to install, no account. For the English interface add `?lang=en` to the address.

The online version is the whole program, because the whole program is one HTML file. The packages below only exist for people who would rather not open a browser:

| Platform | Package | Notes |
|---|---|---|
| Windows | `Wenpu.exe` | Portable, double-click to run; exports land in `Pictures\Wenpu` |
| Android | `Wenpu.apk` | Standalone app; exports land in `Download/Wenpu`, Android 5.0 and up |
| Linux | `Wenpu-3.3-linux.tar.gz` | Source plus a launcher; opens a window with pywebview, otherwise falls back to the browser |

All three are in [Releases](../../releases). You can also just double-click `index.html` — no install, no network, nothing uploaded.

---

## What it actually solves

Pattern material online has three annoyances: it is usually a bitmap (blurry when enlarged), it wants you to register, or you have to tile it into a seamless repeat yourself.

Wenpu treats a pattern as a **rule**, not an image. Change the cell count, stroke weight or margin and the whole sheet re-lays itself out with edges that always meet. Vector for print shops, PDF at actual size, JPG for a social post.

---

## 378 patterns, every region above fifty

These are not bitmap assets; each one is computed from geometry. Seven regions, at least fifty in each, China the largest at 64. The table shows twelve representatives per region; the full list lives in the app.

| Region | Count | Representative patterns |
|---|---|---|
| **China** | 64 | Meander · Cloud and thunder · Wan fret · Double diamond · Ball lattice · Eight-way lattice · Endless knot · Baoxiang rosette · Scroll vine · Honeysuckle scroll · Waves and rock · Mountain character |
| **Japan** | 54 | Seigaiha · Hemp leaf · Shippo · Ichimatsu check · Sayagata · Kanoko dots · Kikkō · Kagome · Yagasuri · Kozakura · Umebachi · Kōrai border |
| **West & Central Asia** | 52 | Eight-point star · Paisley · Tulip · Kufic band · Mashrabiya · Mihrab arch · Banna'i · Suzani · Ram's horn · Isfahan roundel · Six-point star · Medallion |
| **Europe** | 52 | Celtic knot · Greek key · Fleur-de-lis · Rose window · Acanthus · Damask · Tracery · Imbrication · Selbu snowflake · Rosette · Tartan · Egg-and-dart |
| **Africa** | 52 | Bogolan · Kente · Ethiopian cross · Adinkra · Adinkrahene · Nkonsonkonson · Fihankra · Kuba patch · Egyptian lotus · Tifinagh · Maasai band · Ndebele wall |
| **Americas** | 52 | Inca step · Navajo rug · Maya greca · Chakana · Shipibo · Aztec · Marajoara · Navajo storm · Maya stair · Lakota morning star · Inca sun · Kené |
| **Asia-Pacific** | 52 | Parang · Koru · Rangoli · Kawung · Songket · Kōwhaiwhai · Poleng · Kranok · Rangoli grid · Hawaiian quilt · Đông Sơn spiral · Padma lotus |

**Every pattern carries a note under the canvas**: how the form is built, where it comes from, what it is good for today. Set in body size, not as a footnote. Every note exists in both Chinese and English — translated by hand, not by machine.

---

## Chinese and English

A small button at the right of the menu bar reads `EN` in Chinese and 「中」 in English. One click switches the whole interface:

- **Interface**: use, region, mood, colors, density, aging, repeat, export — all of it
- **Content**: all 378 pattern names, one-line notes, full descriptions and use lists
- **Documents**: Guide, About, License and Disclaimer each have an English version
- **Remembered**: the choice persists to the next visit

The address can pin it: `?lang=en` opens straight into English.

Everything lives inside the same HTML file — there is no external language pack, because it has to run as a single offline file. Interface strings carry `data-zh` / `data-en` attributes; pattern text lives in a `MENU` table keyed by id.

---

## Nine real sizes, plus custom

What comes out is not "a pattern" but an image you can post and a sheet you can print.

| Use | Size | What for |
|---|---|---|
| Phone wallpaper | 1179×2556 | Set it directly |
| Social 3:4 | 1080×1440 | Post cover |
| Social 1:1 | 1080×1080 | Post |
| Business card | 1050×600 | 90×51 mm, printed |
| Bookmark | 591×1772 | 50×150 mm, trim after printing |
| Washi tape | 2126×531 | 180×45 mm repeat, ready for a factory |
| A4 print | 2480×3508 | Wrapping, papercut, tracing |
| Desktop wallpaper | 2560×1440 | 2K |
| Tile asset | 1024×1024 | Web and slide backgrounds, forced seamless with no margin |
| **Custom** | 200–6000 px | Type your own; plus 1:1 / 3:4 / 4:5 / 9:16 / 16:9 / A4 / Card shortcuts |

### Aging

One strength slider: yellowing, paper grain, water stains, darkened corners. 40–60 looks most like old paper. It is computed live rather than laid on as a texture filter — every version changes with the seed.

PNG, JPG, WebP and PDF carry it; SVG is pure vector line art and does not (the interface says so).

### Inscription

Type and it appears; no checkbox needed first. Add a paper slip at the bottom or the top, and a cinnabar seal reading 纹谱 in the lower right.

---

## Six export formats

| Format | When | Measured size (1080×1440) |
|---|---|---|
| **PNG** | Social posts, sharpest lines | 810 KB |
| **JPG** | Smaller file, good enough | 515 KB |
| **WebP** | For the web, smallest | 445 KB |
| **SVG** | Vector; print shops and tape factories want this | 468 KB (2560 paths) |
| **PDF** | 300 dpi at actual size, straight to the printer | one page, embedded JPEG |
| **Transparent PNG** | Lay over your own photos, slides, posters | same as PNG |

Two copy buttons as well: **tile CSS** for web and newsletter builders, and a **color list** with hex values and stroke parameters for designers.

---

## Three real situations

**① I want to draw one.** Turn on the grid: the whole sheet is overlaid with fine squares, every fifth line darker, and the corner reads "cell x mm · N cells". Then turn on the faint guide, and the pattern fades so you can trace straight off the print. Embroidery, woodwork, papercut, journaling — all counted in cells.

**② I want to match something I photographed.** "Pick color from photo". Photograph cloth, brick or old wood, and it reads the dominant colors; one tap sets ink or paper. The image is read locally and never uploaded.

**③ I just want a mood.** Five presets — Quiet, Opulent, Rustic, Cool, Folk. Each is a combination of colors, stroke weight, density and repeat, and one click changes the whole temper.

### Repeat modes

- **Mirror ↔** — adjacent columns mirror each other, so a symmetry axis forms at every seam, like cloth matched at the join
- **Mirror ✥** — mirrored on all four sides, giving a kaleidoscopic symmetry

Under the hood the tile and its mirror are assembled into a double-size super tile and then repeated. At the seam the path is the mirror of the same shape, so continuity is arithmetic, not luck.

---

## Menu bar

Four entries plus a language button:

- **Guide** — three steps to an image, combinations that work, URL parameters
- **About** — what it is, what is included, technical notes, author
- **License** — what MIT lets you do, what to keep
- **Disclaimer** — the nature of the patterns, data handling, printing caveats
- **`EN` / 「中」** — switch interface language

---

## Technical notes

- **Single file**: one `index.html`, about 463 KB including both language sets, no dependencies, no build step, no framework
- **One geometry, two backends**: pattern functions return command arrays (M / L / Q / C / O), and canvas and SVG consume the same path data, so preview and export cannot disagree
- **Why it is seamless**: the tile is built as a 2×2 unit with an extra ring laid around the frame; mirror mode assembles the tile and its reflection into a double super tile
- **Aging uses composite modes**: yellowing as multiply, grain as pattern, vignette as a radial gradient — no per-pixel loop, so even A4 stays in the 100 ms range
- **Language switching does not reload**: control containers are emptied and rebuilt, while the state (pattern, colors, size) stays in memory and localStorage, so the canvas does not flash
- **No library anywhere**: the PDF writer is about 60 lines (one page, embedded JPEG, xref table)

---

## What was actually tested

- **378 patterns, 52–64 per region**, each batch checked by eye in screenshots
- **All 378 English entries translated by hand.** A script verified id-by-id coverage: nothing missing, nothing extra, no leftover Chinese except the deliberate brand glyph 纹 and the 「中」 on the language button
- Bilingual rendering verified from a headless Edge DOM snapshot: 378 buttons in Chinese, 378 in English, with title, note card, group counts and status line all matching
- Switching tested live: one click to English keeps `uses` at 10 buttons (no stacked duplicates) and the canvas caption becomes `Phone wallpaper`; one click back returns `lang` to `zh-CN`
- All four documents checked in both languages: English title `Guide`, opening line `Three steps to an image`; back in Chinese it reads 关于纹谱
- No horizontal overflow at 390 px in either language; long English labels (West & Central Asia, Desktop wallpaper) wrap cleanly
- Size went from 321 KB to 463 KB; the increase is the 378 English notes (about 113 K characters) plus the interface dictionary
- Bugs fixed were all found in screenshots: an off-by-one in a two-line branch broke rendering and left the canvas blank; a pointed-arch arc spanned a whole turn and tangled the arch; density set too high fused hex tiles and lace into solid red; a pointed petal waist too narrow read as a five-point star
- Nine sizes render in 6–40 ms full bleed, A4 the slowest
- SVG validated through DOMParser: 2560 paths in single mode, 468 KB
- PDF structure validated: `%PDF-1.4` header, `%%EOF` trailer, correct xref offsets, `/DCTDecode` present
- Aging at 0 and at 55 shows a clear difference in pixel variance on the same pattern, visible in the exported PNG

## Usage

**Simplest**: open the online address above.

**Offline**: double-click `index.html`; on a phone, copy the file over and open it in a browser.

**Desktop**: on Windows, double-click `Wenpu.exe`. It is not a browser in a wrapper — it runs a read-only local server so the page is served from `http://127.0.0.1` in a proper secure context, and exports go through a local channel straight to `Pictures\Wenpu` instead of the Downloads folder.

**Android**: install `Wenpu.apk`. One permission only (network, for that loopback server); no storage, camera or microphone. Exports land in `Download/Wenpu/`. Settings live in the app's own localStorage and survive a restart.

URL parameters reproduce a pattern, which makes sharing easy:

```
index.html?m=baoxiang&u=xhs34&sym=p4&cells=8&lw=6&lang=en
```

`m` pattern · `u` use · `sym` repeat (p1/p2/p4) · `cells` cell count · `lw` stroke weight · `lang` interface language (zh/en).

---

## Boundaries

- The patterns are **geometric abstractions**, not archaeological reconstructions. What you get is the construction rule of a pattern, not a copy of one object. Dragons, phoenixes, figures and vessels are deliberately absent, because a geometry engine cannot draw their shapes
- English names follow the term used in English-language literature where one exists (meander, kufic, adinkra) and transliterate where none does (tatewaku, elibelinde). The notes are written for general readers, not as an academic citation
- The millimetre figures on the grid assume 300 dpi; check that your printer is not set to "fit to page"
- Text in SVG uses the system Kai face and falls back to Song on machines without it
- The washi tape file is a repeating unit; bleed and spot colors are the factory's job

---

## License

MIT. Free to use, modify and republish, commercial use included.

**The one requirement is that the credit stays.** In the source, in `LICENSE`, and on the About or credits page of any modified version, this line must remain:

```
Copyright (c) 2026 Lanlan Eternal
```

Rename it, republish it — no permission needed, no fee, no obligation to publish your changes. Adding "based on Wenpu" just helps people find their way back; that is courtesy, not a condition. See `NOTICE` for details.

---

© 永远的兰兰 · 兰斋丛编 / © Lanlan Eternal · Lanzhai Collection
