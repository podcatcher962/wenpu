# -*- coding: utf-8 -*-
"""
纹谱 Wenpu · 桌面版壳（Windows / Linux 通用）

页面整个内嵌进可执行文件，启动时在 127.0.0.1 起一个只读 http 服务，
窗口从 http://127.0.0.1:<port>/ 进来 —— 不是 file://，所以 localStorage、
canvas 导出、剪贴板这些全都是正经安全上下文。

导出：页面本来用 <a download> 走 blob 下载。桌面 WebView2 对它的处理
各版本不一（有的静默丢掉），所以这里注入一小段钩子：**只**在
「href 是 blob: 且带 download 属性」时拦下来，自己取字节 POST 给本地
服务落到「图片\纹谱」目录；其它一切点击原样放行（保留回退）。
"""
import os
import sys
import json
import time
import socket
import threading
import argparse
import mimetypes
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import webview

APP = "Wenpu"
VER = "3.3"
TITLE = "纹谱 · 世界纹样生成器"
PORT0 = 38971

# ---------------------------------------------------------------- 路径

def res_dir():
    """内嵌资源目录：onefile 解包目录优先，否则脚本所在目录（开发时退到上级）。"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, "index.html")):
        return here
    return os.path.dirname(here)


def data_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    d = os.path.join(base, APP)
    os.makedirs(d, exist_ok=True)
    return d


def out_dir():
    """导出的图片放这儿。"""
    home = os.path.expanduser("~")
    if os.name == "nt":
        cands = [os.path.join(home, "Pictures", "纹谱")]
    else:
        pic = os.environ.get("XDG_PICTURES_DIR") or os.path.join(home, "Pictures")
        cands = [os.path.join(pic, "wenpu"),
                 os.path.join(home, "图片", "wenpu"),
                 os.path.join(home, ".local", "share", "Wenpu", "export")]
    for d in cands:
        try:
            os.makedirs(d, exist_ok=True)
            return d
        except Exception:
            continue
    d = os.path.join(data_dir(), "export")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- 单实例

def acquire_lock():
    """文件锁。已有实例在跑就返回 None（让用户看到「已在运行」而不是开出两个窗口）。"""
    path = os.path.join(data_dir(), "app.lock")
    f = open(path, "a+")
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except Exception:
        f.close()
        return None
    return f


# ---------------------------------------------------------------- 注入脚本

def hook_js(token):
    return (
        "<script>window.__WENPU_APP__=" + json.dumps(
            {"app": "wenpu", "ver": VER, "desktop": True}) + ";</script>"
        "<script>(function(){"
        "if(window.__wpSave)return;window.__wpSave=1;"
        "var TK=" + json.dumps(token) + ";"
        "var say=function(m){try{if(typeof flash==='function')flash(m);}catch(e){}};"
        "var orig=HTMLAnchorElement.prototype.click;"
        "function back(el,why){say('没存成（'+why+'），已改走原来的方式');"
        " try{orig.apply(el,[]);}catch(e){}}"
        "HTMLAnchorElement.prototype.click=function(){"
        "  try{var h=this.href||'';var nm=this.getAttribute('download');"
        "    if(nm&&h.indexOf('blob:')===0){"
        "      var el=this;say('正在存……');"
        "      fetch(h).then(function(r){return r.blob();}).then(function(b){"
        "        return fetch('/__save?token='+TK+'&name='+encodeURIComponent(nm),"
        "          {method:'POST',body:b,headers:{'Content-Type':'application/octet-stream'}});"
        "      }).then(function(r){return r.text();}).then(function(t){"
        "        if(t.indexOf('ok:')===0) say('已存到 '+t.slice(3));"
        "        else back(el,t.slice(0,40));"
        "      }).catch(function(e){back(el,'连不上本地服务');});"
        "      return;"
        "    }}catch(e){}"
        "  return orig.apply(this,arguments);"
        "};"
        "})();</script>"
    )


def beacon_js():
    """就绪信标：让页面自己回敲本地服务。不靠 evaluate_js，也不靠截图。"""
    return (
        "<script>(function(){function p(t){try{"
        "var d={tag:t,rs:document.readyState,title:document.title,"
        "ver:(window.__WENPU_APP__||{}).ver||'',"
        "chips:document.querySelectorAll('.mchip').length,"
        "groups:document.querySelectorAll('.msub').length,"
        "nodes:document.querySelectorAll('*').length,"
        "body:document.body?document.body.childElementCount:0,"
        "proto:location.protocol,"
        "st:Math.round(performance.now()),w:innerWidth,h:innerHeight};"
        "fetch('/rdy?d='+encodeURIComponent(JSON.stringify(d)));}catch(e){}}"
        "p('boot');"
        "document.addEventListener('DOMContentLoaded',function(){p('dcl');});"
        "window.addEventListener('load',function(){p('load');});"
        "setTimeout(function(){p('t3');},3000);"
        "})();</script>"
    )


# ---------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    page = b""
    token = ""
    outdir = ""
    beacon_file = None

    def log_message(self, *a):
        pass

    # ---- 工具

    def _send(self, code, body, ctype="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _q(self, key):
        from urllib.parse import parse_qs, urlparse
        v = parse_qs(urlparse(self.path).query).get(key)
        return v[0] if v else None

    # ---- GET

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/rdy":
            v = self._q("d")
            if v and Handler.beacon_file:
                try:
                    with open(Handler.beacon_file, "a", encoding="utf-8") as f:
                        f.write(v.replace("\n", " ") + "\n")
                except Exception:
                    pass
            self._send(200, b"ok")
            return
        if path in ("/", "/index.html"):
            body = self.page
            js = hook_js(self.token).encode("utf-8")
            if Handler.beacon_file:
                js += beacon_js().encode("utf-8")
            i = body.rfind(b"</head>")
            body = (body[:i] + js + body[i:]) if i > 0 else (js + body)
            self._send(200, body, "text/html; charset=utf-8")
            return
        self._send(404, b"not found")

    def do_HEAD(self):
        self.do_GET()

    # ---- POST /__save

    def do_POST(self):
        if self.path.split("?")[0] != "/__save":
            self._send(404, b"not found")
            return
        if self._q("token") != self.token:
            self._send(403, b"token")
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except Exception:
            n = 0
        if n <= 0 or n > 200 * 1024 * 1024:
            self._send(413, b"size")
            return

        name = os.path.basename(self._q("name") or "")
        name = "".join(c for c in name if ord(c) >= 32 and c not in '\\/:*?"<>|').strip()
        while name.startswith("."):
            name = name[1:]
        if not name or len(name) > 120:
            self._send(400, b"name")
            return

        dst = os.path.join(self.outdir, name)
        base, ext = os.path.splitext(name)
        k = 2
        while os.path.exists(dst) and k < 500:
            dst = os.path.join(self.outdir, "%s (%d)%s" % (base, k, ext))
            k += 1

        left = n
        try:
            with open(dst, "wb") as f:
                while left > 0:
                    buf = self.rfile.read(min(65536, left))
                    if not buf:
                        break
                    f.write(buf)
                    left -= len(buf)
        except Exception:
            self._send(500, b"write")
            return
        self._send(200, ("ok:" + dst).encode("utf-8"))


def serve(port=None):
    Handler.page = open(os.path.join(res_dir(), "index.html"), "rb").read()
    Handler.token = "%s-%s" % (os.getpid(), int(time.time() * 1000))
    Handler.outdir = out_dir()

    ports = [port] if port else list(range(PORT0, PORT0 + 12)) + [0]
    for p in ports:
        try:
            # allow_reuse_address=False：否则端口被占时 bind 也会成功，
            # 但一个请求都收不到 —— 表现为窗口开了、页面空白。
            ThreadingHTTPServer.allow_reuse_address = False
            srv = ThreadingHTTPServer(("127.0.0.1", p), Handler)
        except Exception:
            continue
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        return srv, srv.server_address[1]
    raise RuntimeError("找不到可用端口")


# ---------------------------------------------------------------- 自检

def selftest():
    import urllib.request
    rep = []
    ok = True

    html = os.path.join(res_dir(), "index.html")
    ent = os.path.exists(html)
    size = os.path.getsize(html) if ent else 0
    rep.append(("内嵌页面存在", ent, "%s (%d 字节)" % (html, size)))
    ok = ok and ent and size > 100000
    if not ent:
        return ok, rep

    srv, port = serve(0)
    url = "http://127.0.0.1:%d/" % port
    try:
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        raw = op.open(url, timeout=10).read()
        src = open(html, "rb").read()
        injected = b"__WENPU_APP__" in raw
        grew = len(raw) > len(src)
        rep.append(("本地服务可访问", True, "%s -> %d 字节" % (url, len(raw))))
        rep.append(("注入桌面标记", injected and grew, "+%d 字节" % (len(raw) - len(src))))
        ok = ok and injected and grew
        # 页面结构抽检
        for kw, why in [(b"MOTIFS", "图案元素表"), (b"gen:", "生成器"), (b"canvas", "画布")]:
            hit = kw in src
            rep.append(("页面含" + why, hit, kw.decode()))
            ok = ok and hit
        # 404
        try:
            op.open(url + "nope.js", timeout=5)
            rep.append(("陌生路径给 404", False, "居然 200"))
            ok = False
        except Exception as e:
            code = getattr(e, "code", 0)
            rep.append(("陌生路径给 404", code == 404, "HTTP %s" % code))
            ok = ok and code == 404
        # 导出目录
        d = out_dir()
        rep.append(("导出目录可写", os.access(d, os.W_OK), d))
        ok = ok and os.access(d, os.W_OK)
    finally:
        srv.shutdown()
    return ok, rep


def domcheck(out_path):
    """在窗口进程里验 DOM（不开 CDP）。"""
    guard_t = threading.Thread(target=_guard, args=(out_path,), daemon=True)
    guard_t.start()
    srv, port = serve()
    state = {"ok": False}

    def worker(win):
        try:
            time.sleep(2.0)
            js = """(function(){
              var o={};
              o.rs=document.readyState;
              o.proto=location.protocol;
              o.mark=!!(window.__WENPU_APP__&&window.__WENPU_APP__.desktop);
              o.title=document.title;
              o.chips=document.querySelectorAll('.mchip').length;
              o.groups=document.querySelectorAll('.msub').length;
              o.canvas=document.querySelectorAll('canvas').length;
              o.nodes=document.querySelectorAll('*').length;
              o.know=(document.querySelector('.know')||{}).textContent||'';
              o.w=innerWidth; o.h=innerHeight;
              return JSON.stringify(o);
            })()"""
            raw = win.evaluate_js(js)
            d = json.loads(raw) if isinstance(raw, str) else raw
            d["_ok"] = (d.get("rs") == "complete" and d.get("proto") == "http:"
                        and d.get("mark") and d.get("chips", 0) > 300
                        and d.get("groups") == 7 and d.get("nodes", 0) > 500)
            open(out_path, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
            state["ok"] = True
        except Exception as e:
            open(out_path, "w", encoding="utf-8").write(
                json.dumps({"err": str(e), "tb": traceback.format_exc()}, ensure_ascii=False, indent=1))
        finally:
            try:
                win.destroy()
            except Exception:
                pass

    webview.create_window(TITLE, "http://127.0.0.1:%d/" % port,
                          width=1280, height=860, min_size=(900, 620))
    webview.start(_run_worker, (worker,))
    try:
        srv.shutdown()
    except Exception:
        pass
    return state["ok"]


def _run_worker(worker):
    try:
        win = webview.windows[0]
    except Exception:
        return
    worker(win)


def _guard(path):
    time.sleep(180)
    if not os.path.exists(path):
        try:
            open(path, "w", encoding="utf-8").write('{"err":"domcheck 超过 180 秒未结束"}')
        except Exception:
            pass
    os._exit(9)


def verify(path, wait=50):
    """开窗，靠页面自己回敲的 /rdy 信标证明「真渲染了」，然后退出。

    比 evaluate_js 稳：不经过任何会被安全软件拦的求值桥。
    比截屏稳：PrintWindow 抓不到 WebView2 的合成层，截出来永远是底色。
    """
    try:
        os.remove(path)
    except Exception:
        pass
    Handler.beacon_file = path
    srv, port = serve()

    def watch():
        t0 = time.time()
        while time.time() - t0 < wait:
            try:
                txt = open(path, encoding="utf-8").read()
                if '"t3"' in txt:
                    data = [json.loads(l) for l in txt.strip().split("\n") if l.strip()]
                    tags = [d.get("tag") for d in data]
                    last = data[-1]
                    ok = (last.get("rs") == "complete"
                          and last.get("proto") == "http:"
                          and last.get("groups") == 7
                          and last.get("chips", 0) >= 370
                          and last.get("nodes", 0) > 500)
                    out = {"ok": ok, "tags": tags, "last": last}
                    if not ok:
                        out["why"] = ("readyState=%s proto=%s groups=%s chips=%s nodes=%s"
                                      % (last.get("rs"), last.get("proto"),
                                         last.get("groups"), last.get("chips"), last.get("nodes")))
                    open(path + ".verdict", "w", encoding="utf-8").write(
                        json.dumps(out, ensure_ascii=False, indent=1))
                    os._exit(0 if ok else 3)
            except Exception:
                pass
            time.sleep(0.4)
        try:
            body = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        except Exception:
            body = ""
        open(path + ".verdict", "w", encoding="utf-8").write(
            json.dumps({"ok": False, "err": "信标超时（未收到 t3）", "raw": body[:400]},
                       ensure_ascii=False, indent=1))
        os._exit(4)

    threading.Thread(target=watch, daemon=True).start()
    webview.create_window(TITLE, "http://127.0.0.1:%d/" % port,
                          width=1280, height=880, on_top=True)
    webview.start(private_mode=False,
                  storage_path=os.path.join(data_dir(), "webview"))


# ---------------------------------------------------------------- 主程序

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--domcheck", metavar="FILE")
    ap.add_argument("--verify", metavar="FILE")
    ap.add_argument("--out", default="")
    ap.add_argument("--port", type=int, default=0)
    a = ap.parse_args()

    if a.selftest:
        ok, rep = selftest()
        lines = ["纹谱自检 %s" % ("全部通过" if ok else "有问题")]
        for name, good, info in rep:
            lines.append("  %s %s  %s" % ("[OK]" if good else "[!!]", name, info))
        txt = "\n".join(lines)
        print(txt)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(txt + "\n")
        sys.exit(0 if ok else 1)

    if a.domcheck:
        ok = domcheck(a.domcheck)
        sys.exit(0 if ok else 1)

    if a.verify:
        verify(a.verify)
        return

    lock = acquire_lock()
    if lock is None:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, "纹谱已经在运行了。", "纹谱", 0x40)
        except Exception:
            print("already running")
        return

    srv, port = serve(a.port or None)
    webview.create_window(
        TITLE,
        "http://127.0.0.1:%d/" % port,
        width=1280, height=880,
        min_size=(900, 620),
        background_color="#F2E6CD",
    )
    webview.start(
        private_mode=False,
        storage_path=os.path.join(data_dir(), "webview"),
    )
    try:
        srv.shutdown()
    except Exception:
        pass


if __name__ == "__main__":
    main()
