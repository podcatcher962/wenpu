#!/usr/bin/env bash
# 纹谱 Wenpu - Linux 启动脚本
#
#   ./run.sh                有 pywebview 就开窗口，没有就用系统浏览器打开
#   ./run.sh --install-deps 装 pywebview（pip --user）
#   ./run.sh --browser      强制用浏览器
#
set -u
cd "$(dirname "$0")" || exit 1

APP="纹谱"
HTML="index.html"

if [ ! -f "$HTML" ]; then
  echo "找不到 $HTML，这个包不完整。"
  exit 1
fi

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done

case "${1:-}" in
  --install-deps)
    if [ -z "$PY" ]; then echo "没找到 python3，先装它。"; exit 1; fi
    echo "装 pywebview（只装到用户目录，不动系统）……"
    "$PY" -m pip install --user --upgrade pywebview || {
      echo
      echo "pip 失败。多数发行版还要先装 WebKit 的 Python 绑定："
      echo "  Debian / Ubuntu : sudo apt install python3-gi gir1.2-webkit2-4.1"
      echo "  Fedora          : sudo dnf install python3-gobject webkit2gtk4.1"
      echo "  Arch            : sudo pacman -S python-gobject webkit2gtk-4.1"
      exit 1
    }
    echo "装好了，再跑一次 ./run.sh"
    exit 0
    ;;
  --browser) OPEN_BROWSER=1 ;;
  *)         OPEN_BROWSER=0 ;;
esac

if [ "$OPEN_BROWSER" = "0" ] && [ -n "$PY" ] && "$PY" -c "import webview" >/dev/null 2>&1; then
  exec "$PY" wenpu.py
fi

# 降级：交给系统浏览器。页面本身是单文件、离线可用，功能一样全。
URL="file://$(pwd)/$HTML"
echo "$APP：用浏览器打开（没有 pywebview，或者你选了 --browser）"
echo "  想换成独立窗口：./run.sh --install-deps"
echo
if command -v xdg-open >/dev/null 2>&1; then
  exec xdg-open "$URL"
elif command -v gio >/dev/null 2>&1; then
  exec gio open "$URL"
elif command -v sensible-browser >/dev/null 2>&1; then
  exec sensible-browser "$URL"
elif command -v firefox >/dev/null 2>&1; then
  exec firefox "$URL"
else
  echo "没找到能打开网页的程序。手动打开这个文件："
  echo "  $URL"
fi
