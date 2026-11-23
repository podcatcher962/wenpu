# -*- coding: utf-8 -*-
"""打 Linux 源码包：Wenpu-<ver>-linux.tar.gz

PyInstaller 不能交叉编译，所以在 Windows 上做不出 Linux 可执行文件。
这里给的是「源码 + 启动脚本」：任何发行版都能跑，不挑 glibc。
"""
import os
import io
import sys
import tarfile
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VER = "3.3"
TOP = "wenpu-" + VER
OUT = os.path.join(ROOT, "dist_linux", "Wenpu-%s-linux.tar.gz" % VER)

FILES = [
    ("index.html",      os.path.join(ROOT, "index.html"),            0o644),
    ("wenpu.py",        os.path.join(ROOT, "desktop", "app.py"),     0o644),
    ("run.sh",          os.path.join(HERE, "run.sh"),                0o755),
    ("README.md",       os.path.join(HERE, "README-linux.md"),       0o644),
    ("LICENSE",         os.path.join(ROOT, "LICENSE"),               0o644),
    ("NOTICE",          os.path.join(ROOT, "NOTICE"),                0o644),
]


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with tarfile.open(OUT, "w:gz", compresslevel=9) as tf:
        # 顶层目录
        ti = tarfile.TarInfo(TOP)
        ti.type = tarfile.DIRTYPE
        ti.mode = 0o755
        ti.mtime = 1795000000
        tf.addfile(ti)
        for name, src, mode in FILES:
            data = open(src, "rb").read()
            ti = tarfile.TarInfo(TOP + "/" + name)
            ti.size = len(data)
            ti.mode = mode
            ti.mtime = 1795000000
            ti.uid = ti.gid = 1000
            ti.uname = ti.gname = "wenpu"
            tf.addfile(ti, io.BytesIO(data))
    return OUT


def verify(path):
    ok = True
    print("\n=== 校验 ===")
    with tarfile.open(path, "r:gz") as tf:
        names = tf.getnames()
        for need in [TOP, TOP + "/index.html", TOP + "/wenpu.py",
                     TOP + "/run.sh", TOP + "/LICENSE", TOP + "/NOTICE"]:
            hit = need in names
            print("  %s %-40s" % ("[OK]" if hit else "[!!]", need))
            ok = ok and hit
        run = tf.getmember(TOP + "/run.sh")
        exec_ok = bool(run.mode & 0o111)
        print("  %s %-40s mode=%o" % ("[OK]" if exec_ok else "[!!]",
                                      "run.sh 有可执行位", run.mode))
        ok = ok and exec_ok
        h = hashlib.sha256(tf.extractfile(TOP + "/index.html").read()).hexdigest()
    src = hashlib.sha256(open(os.path.join(ROOT, "index.html"), "rb").read()).hexdigest()
    same = h == src
    print("  %s %-40s %s" % ("[OK]" if same else "[!!]", "index.html 与源文件一致", h[:16]))
    ok = ok and same
    size = os.path.getsize(path)
    print("  %s %-40s %.1f KB" % ("[OK]" if size < 3 * 1024 * 1024 else "[!!]",
                                  "成品体积", size / 1024))
    print("\n%s" % ("全部通过" if ok else "有问题"))
    return ok


if __name__ == "__main__":
    p = build()
    ok = verify(p)
    print("\n产物:", p)
    sys.exit(0 if ok else 2)
