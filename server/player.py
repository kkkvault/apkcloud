#!/usr/bin/env python3
# APK Long Player - local control server (stdlib only, no pip install needed)
# Listens on 127.0.0.1 by default. Set APK_PLAYER_HOST=0.0.0.0 ONLY if you
# understand that your local network can then reach this panel.
# This server does NOT run Android itself. It drives an emulator that is
# already running on this PC (Android Studio AVD) via adb, and launches
# scrcpy for the real screen. That is why play time is unlimited:
# there is no per-minute cloud meter, only your own PC staying on.
import json, os, re, subprocess, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
HOST = os.environ.get("APK_PLAYER_HOST", "127.0.0.1")
PORT = int(os.environ.get("APK_PLAYER_PORT", "8000"))
MAX_APK = 500 * 1024 * 1024

def run(cmd, timeout=180):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except FileNotFoundError as e:
        return 127, "NOT FOUND: %s - install it and add it to PATH" % e.filename
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after %ss" % timeout

def safe_name(name):
    name = Path(name).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name.lower().endswith(".apk"):
        name += ".apk"
    return name or "app.apk"

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        sys.stderr.write("%s %s\n" % (self.address_string(), a[0] if a else ""))

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path, ctype):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/panel.html"):
            self.send_file(BASE / "panel.html", "text/html; charset=utf-8")
        elif self.path == "/api/status":
            code, out = run(["adb", "devices", "-l"], timeout=20)
            devices = []
            if code == 0:
                for line in out.splitlines()[1:]:
                    if line.strip():
                        devices.append(line.strip())
            self.send_json({"adb_found": code != 127, "devices": devices, "raw": out})
        elif self.path == "/api/apps":
            code, out = run(["adb", "shell", "pm", "list", "packages"], timeout=60)
            pkgs = []
            if code == 0:
                for line in out.splitlines():
                    if line.startswith("package:"):
                        pkgs.append(line[8:].strip())
            self.send_json({"packages": pkgs[:500], "raw": out[:2000]})
        else:
            self.send_response(404); self.end_headers()

    def read_json(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(n) if n else b""
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return {}

    def do_POST(self):
        if self.path == "/api/upload":
            self.handle_upload(); return
        body = self.read_json()
        if self.path == "/api/install":
            name = safe_name(body.get("file", ""))
            target = UPLOADS / name
            if not target.exists():
                self.send_json({"ok": False, "error": "file not found: " + name}, 400); return
            code, out = run(["adb", "install", "-r", str(target)], timeout=300)
            self.send_json({"ok": code == 0, "output": out})
        elif self.path == "/api/launch":
            pkg = re.sub(r"[^A-Za-z0-9._]", "", body.get("package", ""))
            if not pkg:
                self.send_json({"ok": False, "error": "package is empty"}, 400); return
            code, out = run(["adb", "shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"], timeout=60)
            self.send_json({"ok": code == 0, "output": out})
        elif self.path == "/api/scrcpy":
            exe = "scrcpy.exe" if os.name == "nt" else "scrcpy"
            try:
                subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.send_json({"ok": True, "output": "scrcpy started"})
            except FileNotFoundError:
                self.send_json({"ok": False, "error": "scrcpy not found. Run setup.bat (winget install Genymobile.scrcpy) or put scrcpy in PATH."}, 400)
        else:
            self.send_response(404); self.end_headers()

    def handle_upload(self):
        ctype = self.headers.get("Content-Type", "")
        m = re.search(r"boundary=([^;]+)", ctype)
        if not m:
            self.send_json({"ok": False, "error": "multipart boundary missing"}, 400); return
        boundary = m.group(1).strip().strip('"').encode()
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n > MAX_APK + 1024 * 1024:
            self.send_json({"ok": False, "error": "APK too large (limit 500MB)"}, 400); return
        raw = self.rfile.read(n) if n else b""
        # Minimal multipart parser: single file part.
        parts = raw.split(b"--" + boundary)
        saved = None
        for part in parts:
            if b"filename=" not in part:
                continue
            head, _, body = part.partition(b"\r\n\r\n")
            if not body:
                continue
            fn = re.search(rb'filename="([^"]*)"', head)
            name = safe_name((fn.group(1).decode("utf-8", "ignore") if fn else "app.apk"))
            # strip trailing CRLF before next boundary
            if body.endswith(b"\r\n"):
                body = body[:-2]
            target = UPLOADS / name
            target.write_bytes(body)
            saved = name
            break
        if saved:
            self.send_json({"ok": True, "file": saved, "size": (UPLOADS / saved).stat().st_size})
        else:
            self.send_json({"ok": False, "error": "no file part found"}, 400)

if __name__ == "__main__":
    print("APK Long Player panel: http://%s:%d/  (localhost only by default)" % (HOST, PORT))
    print("Uploads folder:", UPLOADS)
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
