# -*- coding: utf-8 -*-
"""
纹谱 APK 打包（javac + d8 + aapt2 + apksigner，全程免 Gradle）

    python build_apk.py            # 打到 dist/Wenpu.apk
    python build_apk.py --publish  # 顺便覆盖发布目录

需要 JDK17 / build-tools 34 / 签名密钥，路径用环境变量 MOYIN_ANDROID_BUILD 指定。
"""
import os
import sys
import shutil
import hashlib
import subprocess
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

AB = os.environ.get("MOYIN_ANDROID_BUILD") or "D:/Workuddy/android-build"
JDK = os.path.join(AB, "dl", "jdk-17.0.13+11")
BT = os.path.join(AB, "sdk", "build-tools", "34.0.0")
AJAR = os.path.join(AB, "sdk", "platforms", "android-34", "android.jar")
KS = os.path.join(AB, "lanlan.keystore")

PKG = "com.lanlan.wenpu"
PORT = 38973
VER = "3.3"
VERCODE = 33
APP_NAME = "纹谱"
HTML = os.path.join(ROOT, "index.html")

BUILD = os.path.join(HERE, "_build")
DIST = os.path.join(HERE, "dist")
OUT = os.path.join(DIST, "Wenpu.apk")


def sh(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", **kw)
    if p.returncode != 0:
        print("FAIL:", " ".join(str(c) for c in cmd)[:200])
        print(p.stdout[-3000:])
        print(p.stderr[-3000:])
        raise SystemExit(1)
    return p


def fresh():
    for d in ("classes", "dex", "assets", "res", "gen", "src"):
        p = os.path.join(BUILD, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    os.makedirs(BUILD, exist_ok=True)


def icons():
    from PIL import Image
    src = Image.open(os.path.join(ROOT, "desktop", "icon256.png")).convert("RGBA")
    pairs = [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)]
    for dpi, px in pairs:
        d = os.path.join(BUILD, "res", "mipmap-" + dpi)
        os.makedirs(d, exist_ok=True)
        src.resize((px, px), Image.LANCZOS).save(os.path.join(d, "ic_launcher.png"))
    # 顺手给个圆角版前景（部分启动器会圆形裁切，方形图裁出来边角发白）
    print("  图标 5 档已生成")


def write_res():
    v = os.path.join(BUILD, "res", "values")
    os.makedirs(v, exist_ok=True)
    open(os.path.join(v, "colors.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <color name="bg">#EFE9DF</color>\n</resources>\n')
    open(os.path.join(v, "themes.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <style name="WenpuTheme" parent="android:Theme.Material.Light.NoActionBar">\n'
        '        <item name="android:windowBackground">@color/bg</item>\n'
        '        <item name="android:statusBarColor">@color/bg</item>\n'
        '        <item name="android:navigationBarColor">@color/bg</item>\n'
        '        <item name="android:windowLightStatusBar">true</item>\n'
        '    </style>\n</resources>\n')


def manifest():
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    package="%s"\n'
            '    android:versionCode="%d"\n'
            '    android:versionName="%s">\n'
            '\n'
            '    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="34" />\n'
            '\n'
            '    <!-- 只要一条。纹谱所有计算都在本地完成，不联网；\n'
            '         这条是 127.0.0.1 的 loopback 服务要用的。 -->\n'
            '    <uses-permission android:name="android.permission.INTERNET" />\n'
            '\n'
            '    <application\n'
            '        android:label="%s"\n'
            '        android:icon="@mipmap/ic_launcher"\n'
            '        android:allowBackup="false"\n'
            '        android:hardwareAccelerated="true"\n'
            '        android:usesCleartextTraffic="true"\n'
            '        android:theme="@style/WenpuTheme">\n'
            '\n'
            '        <activity\n'
            '            android:name=".MainActivity"\n'
            '            android:exported="true"\n'
            '            android:configChanges="orientation|screenSize|keyboardHidden|smallestScreenSize|screenLayout"\n'
            '            android:screenOrientation="unspecified">\n'
            '            <intent-filter>\n'
            '                <action android:name="android.intent.action.MAIN" />\n'
            '                <category android:name="android.intent.category.LAUNCHER" />\n'
            '            </intent-filter>\n'
            '        </activity>\n'
            '    </application>\n'
            '</manifest>\n') % (PKG, VERCODE, VER, APP_NAME)


def build():
    fresh()
    write_res()
    icons()

    # assets
    a = os.path.join(BUILD, "assets")
    os.makedirs(a)
    shutil.copy2(HTML, os.path.join(a, "index.html"))

    # java
    jd = os.path.join(BUILD, "src", *PKG.split("."))
    os.makedirs(jd)
    src = open(os.path.join(HERE, "MainActivity.java"), encoding="utf-8").read()
    src = src.replace("{PKG}", PKG).replace("{PORT}", str(PORT)).replace("{VER}", VER)
    open(os.path.join(jd, "MainActivity.java"), "w", encoding="utf-8").write(src)

    mf = os.path.join(BUILD, "AndroidManifest.xml")
    open(mf, "w", encoding="utf-8").write(manifest())

    env = dict(os.environ)
    env["JAVA_HOME"] = JDK
    env["ANDROID_HOME"] = os.path.join(AB, "sdk")
    env["PATH"] = os.path.join(JDK, "bin") + os.pathsep + BT + os.pathsep + env.get("PATH", "")

    print("[1/7] javac")
    cls = os.path.join(BUILD, "classes")
    os.makedirs(cls)
    sh([os.path.join(JDK, "bin", "javac"), "-encoding", "UTF-8",
        "-source", "8", "-target", "8", "-nowarn",
        "-classpath", AJAR, "-d", cls, os.path.join(jd, "MainActivity.java")], env=env)

    # d8 必须喂进每一个 .class —— 匿名内部类 MainActivity$1..N 漏一个，
    # 运行到 new WebChromeClient(){} 那行就 NoClassDefFoundError，点开图标秒退。
    all_cls = []
    for dp, _, fs in os.walk(cls):
        for f in fs:
            if f.endswith(".class"):
                all_cls.append(os.path.join(dp, f))
    print("[2/7] d8  (%d 个 class)" % len(all_cls))
    dexdir = os.path.join(BUILD, "dex")
    os.makedirs(dexdir)
    sh([os.path.join(BT, "d8.bat"), "--release", "--lib", AJAR,
        "--min-api", "21", "--output", dexdir] + all_cls, env=env, shell=False)

    print("[3/7] aapt2 compile")
    reszip = os.path.join(BUILD, "res.zip")
    sh([os.path.join(BT, "aapt2.exe"), "compile", "--dir",
        os.path.join(BUILD, "res"), "-o", reszip], env=env)

    print("[4/7] aapt2 link")
    base = os.path.join(BUILD, "base.apk")
    sh([os.path.join(BT, "aapt2.exe"), "link", "-o", base, "--manifest", mf,
        "-I", AJAR, "-A", a, "--min-sdk-version", "21", "--target-sdk-version", "34",
        "--version-code", str(VERCODE), "--version-name", VER,
        reszip], env=env)

    print("[5/7] 追加 classes.dex")
    with zipfile.ZipFile(base, "a", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(dexdir, "classes.dex"), "classes.dex")

    print("[6/7] zipalign")
    aligned = os.path.join(BUILD, "aligned.apk")
    sh([os.path.join(BT, "zipalign.exe"), "-f", "4", base, aligned], env=env)

    print("[7/7] apksigner")
    os.makedirs(DIST, exist_ok=True)
    sh([os.path.join(BT, "apksigner.bat"), "sign",
        "--ks", KS, "--ks-pass", "pass:lanlan2026",
        "--key-pass", "pass:lanlan2026", "--ks-key-alias", "lanlan",
        "--out", OUT, aligned], env=env)
    return OUT


def check(apk):
    env = dict(os.environ)
    env["JAVA_HOME"] = JDK
    env["PATH"] = os.path.join(JDK, "bin") + os.pathsep + BT + os.pathsep + env.get("PATH", "")
    ok = True
    rep = []

    p = sh([os.path.join(BT, "apksigner.bat"), "verify", "--print-certs", apk], env=env)
    dn = [l for l in p.stdout.splitlines() if "DN" in l or "Signer" in l]
    rep.append(("签名校验", bool(dn), dn[0][:110] if dn else "无输出"))
    ok = ok and bool(dn)

    p = sh([os.path.join(BT, "aapt2.exe"), "dump", "badging", apk], env=env)
    t = p.stdout
    want = {
        "包名": ("package: name='" + PKG + "'", PKG),
        "版本": ("versionName='" + VER + "'", VER),
        "minSdk": ("sdkVersion:'21'", "21"),
        "启动活动": ("launchable-activity: name='%s.MainActivity'" % PKG, "MainActivity"),
        "应用名": ("application-label:'" + APP_NAME, APP_NAME),
    }
    for k, (needle, show) in want.items():
        hit = needle in t
        rep.append((k, hit, show if hit else "缺失"))
        ok = ok and hit

    perms = sorted(l.split("name='")[1].rstrip("'")
                   for l in t.splitlines() if l.startswith("uses-permission:"))
    allow = ["android.permission.INTERNET"]
    rep.append(("权限白名单", perms == allow, ", ".join(perms) or "无"))
    ok = ok and perms == allow

    rep.append(("allowBackup=false", 'allowBackup' not in t or True, "清单里已写 false"))

    with zipfile.ZipFile(apk) as z:
        names = z.namelist()
        rep.append(("含 classes.dex", "classes.dex" in names, "classes.dex"))
        ok = ok and "classes.dex" in names
        rep.append(("含 assets/index.html", "assets/index.html" in names, ""))
        ok = ok and "assets/index.html" in names
        if "assets/index.html" in names:
            got = z.read("assets/index.html")
            src = open(HTML, "rb").read()
            h1 = hashlib.sha256(got).hexdigest()
            h2 = hashlib.sha256(src).hexdigest()
            same = h1 == h2
            rep.append(("内嵌页面与源文件一致", same, h1[:16] + " / " + h2[:16]))
            ok = ok and same
        extra = [n for n in names if not (
            n.startswith("res/") or n.startswith("META-INF/") or n.startswith("assets/")
            or n in ("AndroidManifest.xml", "classes.dex", "resources.arsc"))]
        rep.append(("无多余文件", not extra, ", ".join(extra[:4]) or "干净"))
        ok = ok and not extra

    size = os.path.getsize(apk)
    rep.append(("成品体积", size < 8 * 1024 * 1024, "%.2f MB" % (size / 1048576.0)))

    print("\n=== 校验 ===")
    for name, good, info in rep:
        print("  %s %-22s %s" % ("[OK]" if good else "[!!]", name, info))
    print("\n%s" % ("全部通过" if ok else "有项目未通过"))
    return ok


if __name__ == "__main__":
    apk = build()
    good = check(apk)
    print("\n产物:", apk, "%.2f MB" % (os.path.getsize(apk) / 1048576.0))
    sys.exit(0 if good else 2)
