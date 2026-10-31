# APK Cloud LITE player - this PC only, no connection, no Docker, no server.
# Virtual tablet: lite AVD (Nexus 10 tablet profile, 1280x800, 1024MB RAM).
# Standard library only. Tkinter window, not a browser panel.
# Low-spec defaults: lite AVD, 1024MB RAM, 720p, scrcpy capped at 720p / 2Mbps.
# Roblox button runs the official Windows client when installed, no emulator needed.
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

ROOT = os.path.dirname(os.path.abspath(__file__))
SDK = os.path.join(ROOT, "sdk")
BIN_DIRS = [
    os.path.join(SDK, "platform-tools"),
    os.path.join(SDK, "emulator"),
    os.path.join(SDK, "cmdline-tools", "latest", "bin"),
]
os.environ["PATH"] = os.pathsep.join(BIN_DIRS + [os.environ.get("PATH", "")])

APK = {"path": ""}


def run(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


def find_roblox():
    base = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions")
    if not os.path.isdir(base):
        return ""
    for d in sorted(os.listdir(base), reverse=True):
        p = os.path.join(base, d, "RobloxPlayerBeta.exe")
        if os.path.isfile(p):
            return p
    return ""


def start_emulator(gpu_mode):
    # gpu_mode: swiftshader_indirect = stable on PCs without a good GPU,
    # auto = faster when a GPU exists. Both use the same lite AVD.
    cmd = (
        f'start "" emulator -avd lite -memory 1024 -cores 2 '
        f"-gpu {gpu_mode} -partition-size 1024 -no-snapshot-load"
    )
    run(cmd)
    log("Emulator started in " + gpu_mode + " mode. Wait for the home screen.")


def check_device():
    r = run("adb devices")
    log(r.stdout or "(no adb output)")
    r = run("adb shell getprop sys.boot_completed")
    log("boot_completed: " + (r.stdout.strip() or "(not ready)"))


def choose_apk():
    p = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
    if p:
        APK["path"] = p
        log("APK: " + p)


def install_apk():
    if not APK["path"]:
        messagebox.showwarning("No APK", "Choose an APK first.")
        return
    r = run(f'adb install -r "{APK["path"]}"')
    log((r.stdout or "") + (r.stderr or ""))


def launch_app(pkg):
    pkg = pkg.strip()
    if not pkg:
        messagebox.showwarning("No package", "Type the package name first.")
        return
    r = run(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
    log((r.stdout or "") + (r.stderr or ""))


def open_scrcpy():
    # Cap resolution and bitrate so a low-spec PC is not overloaded by the mirror itself.
    run('start "" scrcpy --max-size 720 --video-bit-rate 2M')
    log("scrcpy opened (720p, 2Mbps cap).")


def launch_roblox_pc():
    p = find_roblox()
    if not p:
        messagebox.showinfo(
            "Roblox PC client not found",
            "Install the official Windows client from roblox.com first, "
            "then press this button again. No emulator is needed for Roblox.",
        )
        return
    subprocess.Popen([p])
    log("Roblox Windows client started: " + p)


def log(msg):
    box.insert(tk.END, msg + "\n")
    box.see(tk.END)


app = tk.Tk()
app.title("APK Cloud LITE tablet - this PC only, no connection")
app.geometry("620x520")

tk.Button(app, text="1. Start lite emulator (stable, software graphics)",
          command=lambda: start_emulator("swiftshader_indirect")).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="1b. Start lite emulator (fast, GPU if available)",
          command=lambda: start_emulator("auto")).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="2. Check device", command=check_device).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="3. Choose APK", command=choose_apk).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="4. Install APK", command=install_apk).pack(fill="x", padx=8, pady=2)

pkg_var = tk.StringVar()
tk.Entry(app, textvariable=pkg_var).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="5. Launch app (type package name above)",
          command=lambda: launch_app(pkg_var.get())).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="6. Open scrcpy screen (720p cap)",
          command=open_scrcpy).pack(fill="x", padx=8, pady=2)
tk.Button(app, text="Roblox: run official Windows client (no emulator)",
          command=launch_roblox_pc).pack(fill="x", padx=8, pady=6)

box = tk.Text(app, height=16)
box.pack(fill="both", expand=True, padx=8, pady=4)
log("LITE tablet ready. No connection, no Docker, no server in this mode.")
log("If the emulator never boots, BIOS virtualization is the most common cause.")

app.mainloop()
