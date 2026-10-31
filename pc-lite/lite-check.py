# LITE spec check - standard library only, Windows only.
# Prints RAM, CPU cores, free disk, and whether adb/emulator/scrcpy are present.
# It does not change anything. Run: python lite-check.py
import ctypes
import os
import shutil
import sys


def ram_gb():
    try:
        class Mem(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = Mem()
        m.dwLength = ctypes.sizeof(m)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullTotalPhys / (1024 ** 3), m.ullAvailPhys / (1024 ** 3)
    except Exception:
        return None, None


def main():
    total, avail = ram_gb()
    print(f"RAM total: {total:.1f} GB, free: {avail:.1f} GB" if total else "RAM: unknown (not Windows?)")
    print(f"CPU cores: {os.cpu_count()}")
    try:
        free = shutil.disk_usage(os.getcwd()).free / (1024 ** 3)
        print(f"Disk free here: {free:.1f} GB")
    except Exception as e:
        print("Disk: unknown", e)
    for tool in ("python", "java", "adb", "emulator", "scrcpy"):
        print(f"{tool}: {'FOUND' if shutil.which(tool) else 'NOT FOUND'}")
    print()
    if total and total < 4:
        print("Verdict: very low RAM. LITE mode is the only local route, and heavy 3D games will still lag.")
    elif total and total < 8:
        print("Verdict: low-spec. Use LITE mode, 720p, software graphics first.")
    else:
        print("Verdict: LITE mode should boot. Heavy 3D still depends on GPU, not just RAM.")


if __name__ == "__main__":
    main()
