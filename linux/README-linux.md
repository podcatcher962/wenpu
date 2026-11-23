# 纹谱 Wenpu · Linux 版

世界纹样生成器。一个 HTML 文件，加上一层可选的外壳。

## 你拿到的包

```
wenpu-3.2/
├── index.html      整个软件（378 个母题、全部几何与科普，都在这个文件里）
├── wenpu.py        桌面外壳：开窗口、导出图片直接落到 ~/Pictures/wenpu/
├── run.sh          启动脚本（自己挑窗口版还是浏览器版）
├── LICENSE         MIT
└── NOTICE          署名要求
```

## 跑起来

```bash
chmod +x run.sh
./run.sh
```

它会先看有没有 `pywebview`：

- **有** → 开一个无地址栏的独立窗口，导出直接落到 `~/Pictures/wenpu/`
- **没有** → 用系统浏览器打开 `index.html`。功能一样全（导出会进浏览器的下载目录）

想装成独立窗口：

```bash
./run.sh --install-deps
```

多数发行版光装 pywebview 还不够，还要 WebKit 的 Python 绑定：

| 发行版 | 命令 |
|---|---|
| Debian / Ubuntu | `sudo apt install python3-gi gir1.2-webkit2-4.1` |
| Fedora | `sudo dnf install python3-gobject webkit2gtk4.1` |
| Arch | `sudo pacman -S python-gobject webkit2gtk-4.1` |
| openSUSE | `sudo zypper install python3-gobject typelib-1_0-WebKit2-4_1` |

装了还起不来，试 `./run.sh --browser`，浏览器版永远是能用的那条路。

## 说明

- **为什么不给 AppImage**：PyInstaller 不能交叉编译。在 Windows 上打不出 Linux 可执行文件，
  硬塞一个「看起来像」的包只会让人白下载。这个 tar.gz 里是源码 + 脚本，任何发行版都能跑，
  也不会因为 glibc 版本对不上而报错。
- **不联网**：页面加载后没有任何外部请求。纹样全部是几何算出来的，不是图片素材。
- **数据只在本地**：设置存在浏览器的 localStorage；窗口版的 webview 数据在
  `~/.local/share/Wenpu/webview/`。清掉这个目录就是恢复默认。
- **卸载**：删掉这个目录，再删 `~/.local/share/Wenpu/` 就行。

## 许可

MIT。随便用、随便改、随便再发布，含商用。**唯一要求是保留署名**：

```
Copyright (c) 2026 Lanlan Eternal
```

详见 `LICENSE` 与 `NOTICE`。

作者：永远的兰兰 · 兰斋丛编
