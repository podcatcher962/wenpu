package {PKG};

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 纹谱的安卓壳（精简版）。
 *
 * 页面整个内嵌进 assets，启动时在 127.0.0.1 起一个只读 http 服务，
 * 页面从 http://127.0.0.1:<port>/index.html 进来 —— 不是 file://，
 * 所以 localStorage（用户的配色与图案元素选择）是正经的持久化来源，
 * origin 固定为 http://127.0.0.1:{PORT}，关掉再开设置还在。
 *
 * 唯一的写口是 POST /__save：页面的导出走 <a download> + blob，
 * 而安卓 WebView 根本不支持 blob: 下载（setDownloadListener 对 blob:
 * 也不会被调用）。所以由注入脚本拦下来，自己取字节 POST 过来落盘。
 */
public class MainActivity extends Activity {
    private WebView web;
    private ServerSocket server;
    private int port = 0;
    private volatile boolean fellBack = false;
    private volatile boolean pageOk = false;
    private volatile boolean mainErr = false;

    /** 每次启动随机生成，只通过 evaluateJavascript 给内嵌页面。 */
    private String saveToken = null;
    private static final long MAX_SAVE = 200L * 1024 * 1024;
    private static final String OK_EXT = "|png|jpg|jpeg|webp|svg|pdf|txt|json|";

    private android.webkit.ValueCallback<Uri[]> filePathCallback;
    private static final int REQ_FILE = 4001;

    private static final Map<String, String> MIME = new HashMap<String, String>();
    static {
        MIME.put("html", "text/html; charset=utf-8");
        MIME.put("js", "application/javascript; charset=utf-8");
        MIME.put("css", "text/css; charset=utf-8");
        MIME.put("json", "application/json; charset=utf-8");
        MIME.put("png", "image/png");
        MIME.put("ico", "image/x-icon");
        MIME.put("svg", "image/svg+xml");
    }

    @Override
    protected void onCreate(Bundle b) {
        // 连 super 一起包住：资源/主题层面的问题也要显示出来，而不是静默退出
        try {
            super.onCreate(b);
            final String prev = readLastCrash();
            if (prev != null) {
                showText("上一次运行崩了（点屏幕清掉，再进一次）\n\n" + prev, true);
                return;
            }
            init();
        } catch (Throwable t) {
            try {
                saveCrash(t);
                showText("启动失败\n\n" + trace(t), false);
            } catch (Throwable x) { }
        }
    }

    private void init() {
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override
            public void uncaughtException(Thread t, Throwable e) {
                saveCrash(e);
                android.os.Process.killProcess(android.os.Process.myPid());
            }
        });

        saveToken = UUID.randomUUID().toString().replace("-", "")
                  + Long.toHexString(System.nanoTime());

        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // localStorage：用户的设置靠它
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);         // 照片取色要读用户选的 content://
        s.setAllowUniversalAccessFromFileURLs(true);  // 仅为 file:// 兜底保留
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        web.setBackgroundColor(0xFFEFE9DF);

        // 纹谱一次都不用麦克风/摄像头/定位，一律拒绝，不留「默认放行」的后门。
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest r) {
                try { r.deny(); } catch (Throwable t) { }
            }

            /**
             * 「从照片取色」那个 <input type=file> 不接这个回调，点了完全没反应。
             * 只在用户主动点击时开系统选择器；只列图片。
             */
            @Override
            public boolean onShowFileChooser(WebView v,
                    android.webkit.ValueCallback<Uri[]> cb,
                    FileChooserParams params) {
                try {
                    if (filePathCallback != null) filePathCallback.onReceiveValue(null);
                    filePathCallback = cb;
                    Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType("image/*");
                    startActivityForResult(Intent.createChooser(i, "选一张图片"), REQ_FILE);
                    return true;
                } catch (Throwable t) {
                    filePathCallback = null;
                    return false;
                }
            }
        });

        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView v, String url) {
                if (!mainErr) pageOk = true;
                if (url != null && url.startsWith("http://127.0.0.1")) injectSaveHook();
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                String h = u.getHost();
                if (h != null && (h.equals("127.0.0.1") || h.equals("localhost"))) return false;
                String p = u.getScheme();
                if ("file".equals(p)) return false;
                if ("http".equals(p) || "https".equals(p)) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, u)); }
                    catch (Exception e) { }
                    return true;
                }
                return false;
            }

            /** 个别手机的防护会拦 loopback，主框架一旦失败就退回 file://，至少能用。 */
            @Override
            public void onReceivedError(WebView v, WebResourceRequest r,
                                        android.webkit.WebResourceError e) {
                if (r != null && r.isForMainFrame() && !fellBack) {
                    String u = String.valueOf(r.getUrl());
                    mainErr = true;
                    if (u.startsWith("http://127.0.0.1")) {
                        fellBack = true;
                        mainErr = false;
                        v.loadUrl("file:///android_asset/index.html");
                    }
                }
            }
        });

        setContentView(web);

        // bind 必须离开主线程：Android 把 ServerSocket 的 bind 也算网络操作，
        // 主线程上做会 NetworkOnMainThreadException —— 表现是点开图标立刻闪退。
        new Thread(new Runnable() {
            public void run() {
                bindServer();
                final int p = port;
                runOnUiThread(new Runnable() {
                    public void run() {
                        if (p > 0) {
                            web.loadUrl("http://127.0.0.1:" + p + "/index.html");
                            web.postDelayed(new Runnable() {
                                public void run() {
                                    if (!pageOk && !fellBack) {
                                        fellBack = true;
                                        mainErr = false;
                                        web.loadUrl("file:///android_asset/index.html");
                                    }
                                }
                            }, 8000);
                        } else {
                            fellBack = true;
                            mainErr = false;
                            web.loadUrl("file:///android_asset/index.html");
                        }
                    }
                });
            }
        }).start();
    }

    // ── 导出：把页面的 blob 搬进「下载」目录 ─────────────────────────
    private void injectSaveHook() {
        if (saveToken == null) return;
        String js =
            "(function(){"
          + "if(window.__wpSave)return;"
          + "if(location.protocol!=='http:')return;"
          + "window.__wpSave=1;"
          + "window.__WENPU_APP__={app:'wenpu',ver:'{VER}',android:true};"
          + "var TK='" + saveToken + "';"
          + "var say=function(m){try{"
          + "  if(typeof flash==='function'){flash(m);return;} }catch(e){} };"
          + "var orig=HTMLAnchorElement.prototype.click;"
          + "function back(el,why){say('没存成（'+(why||'没连上')+'），已改走原来的方式');"
          + " try{orig.apply(el,[]);}catch(e){}}"
          + "HTMLAnchorElement.prototype.click=function(){"
          + "  try{var h=this.href||'';var nm=this.getAttribute('download');"
          + "    if(nm&&h.indexOf('blob:')===0){"
          + "      var el=this;say('正在存到手机……');"
          + "      fetch(h).then(function(r){return r.blob();}).then(function(b){"
          + "        return fetch('/__save?token='+TK+'&name='+encodeURIComponent(nm),"
          + "          {method:'POST',body:b,headers:{'Content-Type':'application/octet-stream'}});"
          + "      }).then(function(r){return r.text().then(function(t){return {t:t,st:r.status};});})"
          + "      .then(function(o){"
          + "        if(o.t.indexOf('ok:')===0){"
          + "          say('已存到手机：'+o.t.slice(3)+'（文件管理器里找「下载/纹谱」）',5200);"
          + "        } else { back(el, o.st+' '+o.t); }"
          + "      }).catch(function(){ back(el,''); });"
          + "      return;"
          + "    }}catch(e){}"
          + "  return orig.apply(this,arguments);"
          + "};"
          + "})();";
        try { web.evaluateJavascript(js, null); } catch (Throwable t) { }
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        if (req != REQ_FILE) {
            super.onActivityResult(req, res, data);
            return;
        }
        Uri[] out = null;
        try {
            if (res == RESULT_OK && data != null && data.getData() != null) {
                out = new Uri[] { data.getData() };
            }
        } catch (Throwable t) {
            out = null;
        }
        // 无论如何都要回一次，否则页面上那个 input 永远卡在禁用态
        try { if (filePathCallback != null) filePathCallback.onReceiveValue(out); }
        catch (Throwable t) { }
        filePathCallback = null;
    }

    // ── 崩溃自留证：没有 adb 也能把原因显示在屏幕上 ─────────────────
    private String crashFile() {
        return new File(getFilesDir(), "last_crash.txt").getAbsolutePath();
    }

    private static String trace(Throwable t) {
        java.io.StringWriter sw = new java.io.StringWriter();
        t.printStackTrace(new java.io.PrintWriter(sw));
        String s = sw.toString();
        return s.length() > 4000 ? s.substring(0, 4000) : s;
    }

    private void saveCrash(Throwable t) {
        try {
            FileOutputStream fo = new FileOutputStream(crashFile());
            fo.write(trace(t).getBytes("UTF-8"));
            fo.close();
        } catch (Throwable x) { }
    }

    private String readLastCrash() {
        try {
            File f = new File(crashFile());
            if (!f.exists()) return null;
            byte[] buf = new byte[(int) f.length()];
            InputStream in = new java.io.FileInputStream(f);
            int n = in.read(buf);
            in.close();
            return n > 0 ? new String(buf, 0, n, "UTF-8") : null;
        } catch (Throwable x) {
            return null;
        }
    }

    private void showText(String msg, final boolean tapToClear) {
        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(msg);
        tv.setTextSize(11f);
        tv.setTextColor(0xFF26221D);
        tv.setPadding(28, 28, 28, 28);
        sv.setBackgroundColor(0xFFEFE9DF);
        sv.addView(tv);
        if (tapToClear) {
            sv.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    try { new File(crashFile()).delete(); } catch (Throwable x) { }
                    recreate();
                }
            });
        }
        setContentView(sv);
    }

    // ── 极小 HTTP 服务（只读 assets + 一个写口）─────────────────────
    private void bindServer() {
        // 端口固定：origin 稳定，localStorage 才不会每次启动都换一份
        int[] tries = new int[] { {PORT}, 0 };
        for (int i = 0; i < tries.length && server == null; i++) {
            try {
                ServerSocket ss = new ServerSocket(tries[i], 16,
                        InetAddress.getByName("127.0.0.1"));
                server = ss;
                port = ss.getLocalPort();
            } catch (Exception e) {
                server = null;
            }
        }
        if (server == null) { port = 0; return; }
        Thread t = new Thread(new Runnable() {
            public void run() {
                while (true) {
                    Socket c = null;
                    try { c = server.accept(); } catch (Exception e) { continue; }
                    final Socket cs = c;
                    Thread w = new Thread(new Runnable() {
                        public void run() { serve(cs); }
                    }, "wenpu-http");
                    w.setDaemon(true);
                    w.start();
                }
            }
        });
        t.setDaemon(true);
        t.start();
    }

    private static String readHead(InputStream in) throws Exception {
        ByteArrayOutputStream hb = new ByteArrayOutputStream();
        int state = 0, b, n = 0;
        while ((b = in.read()) >= 0) {
            if (++n > 16384) return null;
            hb.write(b);
            if (state == 0 && b == '\r') state = 1;
            else if (state == 1 && b == '\n') state = 2;
            else if (state == 2 && b == '\r') state = 3;
            else if (state == 3 && b == '\n') return hb.toString("UTF-8");
            else state = (b == '\r') ? 1 : 0;
        }
        return null;
    }

    private void serve(Socket c) {
        try {
            c.setSoTimeout(20000);
            InputStream in = c.getInputStream();
            String head = readHead(in);
            if (head == null) { c.close(); return; }
            String[] lines = head.split("\r\n");
            String[] parts = lines[0].split(" ");
            String method = parts.length >= 3 ? parts[0] : "GET";
            String target = parts.length >= 2 ? parts[1] : "/";
            int q = target.indexOf('?');
            String query = q >= 0 ? target.substring(q + 1) : "";
            String path = q >= 0 ? target.substring(0, q) : target;

            if (path.equals("/__save")) { handleSave(c, in, lines, method, query); return; }

            if (!"GET".equals(method) && !"HEAD".equals(method)) { err(c, 405, "只读"); return; }
            if (path.equals("/")) path = "/index.html";
            String rel = path.startsWith("/") ? path.substring(1) : path;
            if (rel.contains("..") || rel.indexOf('\\') >= 0) { err(c, 403, "路径不合法"); return; }

            InputStream a;
            try { a = getAssets().open(rel); }
            catch (Exception e) { err(c, 404, "没有这个文件"); return; }
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[65536];
            int n;
            while ((n = a.read(buf)) > 0) bos.write(buf, 0, n);
            a.close();
            byte[] body = bos.toByteArray();

            String ext = "";
            int d = rel.lastIndexOf('.');
            if (d >= 0) ext = rel.substring(d + 1).toLowerCase();
            String mime = MIME.containsKey(ext) ? MIME.get(ext) : "application/octet-stream";

            OutputStream out = c.getOutputStream();
            out.write(("HTTP/1.1 200 OK\r\nContent-Type: " + mime +
                       "\r\nContent-Length: " + body.length +
                       "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n")
                      .getBytes("UTF-8"));
            out.write(body);
            out.flush();
            c.close();
        } catch (Exception e) {
            try { c.close(); } catch (Exception x) { }
        }
    }

    private void handleSave(Socket c, InputStream in, String[] lines,
                            String method, String query) {
        if (!"POST".equals(method)) { err(c, 405, "只收 POST"); return; }
        String token = qval(query, "token");
        if (saveToken == null || token == null || !saveToken.equals(token)) {
            err(c, 403, "令牌不对");
            return;
        }
        String origin = header(lines, "origin");
        if (origin != null && !origin.equals("http://127.0.0.1:" + port)) {
            err(c, 403, "来源不对");
            return;
        }
        long len;
        try { len = Long.parseLong(String.valueOf(header(lines, "content-length")).trim()); }
        catch (Exception e) { err(c, 411, "缺长度"); return; }
        if (len <= 0 || len > MAX_SAVE) { err(c, 413, "太大或太小"); return; }

        String name = safeName(qval(query, "name"));
        if (name == null) { err(c, 400, "文件名不合法"); return; }

        String where;
        try { where = saveBytes(in, len, name); }
        catch (Throwable t) { err(c, 500, "写不进去"); return; }

        try {
            byte[] bb = ("ok:" + where).getBytes("UTF-8");
            OutputStream out = c.getOutputStream();
            out.write(("HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n"
                     + "Content-Length: " + bb.length + "\r\nConnection: close\r\n\r\n")
                      .getBytes("UTF-8"));
            out.write(bb);
            out.flush();
            c.close();
        } catch (Exception e) {
            try { c.close(); } catch (Exception x) { }
        }
    }

    private static String header(String[] lines, String key) {
        if (lines == null) return null;
        for (int i = 1; i < lines.length; i++) {
            String l = lines[i];
            int e = l.indexOf(':');
            if (e <= 0) continue;
            if (l.substring(0, e).trim().equalsIgnoreCase(key)) return l.substring(e + 1).trim();
        }
        return null;
    }

    private static String qval(String query, String key) {
        if (query == null || query.isEmpty()) return null;
        String[] ps = query.split("&");
        for (String p : ps) {
            int e = p.indexOf('=');
            String k = e >= 0 ? p.substring(0, e) : p;
            if (!k.equals(key)) continue;
            String v = e >= 0 ? p.substring(e + 1) : "";
            try { return java.net.URLDecoder.decode(v, "UTF-8"); }
            catch (Exception x) { return v; }
        }
        return null;
    }

    /** 文件名净化：去控制字符与路径分隔符、剥开头的点、后缀白名单。 */
    private static String safeName(String raw) {
        if (raw == null) return null;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < raw.length() && sb.length() < 90; i++) {
            char ch = raw.charAt(i);
            if (ch < 0x20 || ch == 0x7f) continue;
            if ("\\/:*?\"<>|".indexOf(ch) >= 0) continue;
            sb.append(ch);
        }
        String s = sb.toString().trim();
        while (s.startsWith(".")) s = s.substring(1).trim();
        if (s.length() > 90) s = s.substring(0, 90).trim();
        if (s.isEmpty()) return null;
        int dot = s.lastIndexOf('.');
        String ext = dot > 0 ? s.substring(dot + 1).toLowerCase() : "";
        if (ext.isEmpty()) return null;
        if (OK_EXT.indexOf("|" + ext + "|") < 0) return null;
        return s;
    }

    private static String mimeOf(String name) {
        int d = name.lastIndexOf('.');
        String ext = d > 0 ? name.substring(d + 1).toLowerCase() : "";
        if (ext.equals("json")) return "application/json";
        if (ext.equals("txt")) return "text/plain";
        if (ext.equals("svg")) return "image/svg+xml";
        String m = MIME.get(ext);
        return m != null ? m : "application/octet-stream";
    }

    private static void copy(InputStream in, OutputStream out, long len) throws Exception {
        byte[] buf = new byte[65536];
        long left = len;
        while (left > 0) {
            int n = in.read(buf, 0, (int) Math.min(buf.length, left));
            if (n < 0) break;
            out.write(buf, 0, n);
            left -= n;
        }
    }

    /**
     * 落盘：Android 10+ 写公共「下载/纹谱」，不需要任何权限；
     * 更老的版本退到应用自己的外部目录（同样免权限，卸载即删）。
     */
    private String saveBytes(InputStream in, long len, String name) throws Exception {
        if (android.os.Build.VERSION.SDK_INT >= 29) {
            return Save29.write(this, in, len, name, mimeOf(name));
        }
        File dir = new File(getExternalFilesDir(android.os.Environment.DIRECTORY_DOWNLOADS), "纹谱");
        if (!dir.exists() && !dir.mkdirs()) throw new Exception("建目录失败");
        File f = new File(dir, name);
        String base = name, e = "";
        int d = name.lastIndexOf('.');
        if (d > 0) { base = name.substring(0, d); e = name.substring(d); }
        int i = 2;
        while (f.exists() && i < 100) f = new File(dir, base + " (" + (i++) + ")" + e);
        FileOutputStream fo = new FileOutputStream(f);
        copy(in, fo, len);
        fo.flush();
        fo.close();
        return "Android/data/" + getPackageName() + "/files/Download/纹谱/";
    }

    /** API 29 以上单独放一个类：老机型上根本不会加载它。 */
    private static class Save29 {
        static String write(Activity act, InputStream in, long len,
                            String name, String mime) throws Exception {
            android.content.ContentValues cv = new android.content.ContentValues();
            cv.put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(android.provider.MediaStore.MediaColumns.MIME_TYPE, mime);
            cv.put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH,
                   android.os.Environment.DIRECTORY_DOWNLOADS + "/纹谱");
            cv.put(android.provider.MediaStore.MediaColumns.IS_PENDING, 1);
            Uri item = act.getContentResolver().insert(
                    android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (item == null) throw new Exception("MediaStore 不收");
            OutputStream os = null;
            try {
                os = act.getContentResolver().openOutputStream(item);
                if (os == null) throw new Exception("打不开输出流");
                copy(in, os, len);
                os.flush();
            } catch (Throwable t) {
                try { act.getContentResolver().delete(item, null, null); } catch (Throwable x) { }
                throw new Exception(t);
            } finally {
                try { if (os != null) os.close(); } catch (Throwable x) { }
            }
            android.content.ContentValues done = new android.content.ContentValues();
            done.put(android.provider.MediaStore.MediaColumns.IS_PENDING, 0);
            act.getContentResolver().update(item, done, null, null);
            return "Download/纹谱/";
        }
    }

    private void err(Socket c, int code, String why) {
        try {
            byte[] b = String.valueOf(why).getBytes("UTF-8");
            OutputStream out = c.getOutputStream();
            out.write(("HTTP/1.1 " + code + " Error\r\n"
                     + "Content-Type: text/plain; charset=utf-8\r\n"
                     + "Content-Length: " + b.length + "\r\n"
                     + "Connection: close\r\n\r\n").getBytes("UTF-8"));
            out.write(b);
            out.flush();
            c.close();
        } catch (Exception e) { }
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        try { if (server != null) server.close(); } catch (Exception e) { }
        super.onDestroy();
    }
}
