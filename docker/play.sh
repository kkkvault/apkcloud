#!/bin/bash
# APK Long Player - Docker route (Linux server, or Windows 11 WSL2 with nested virtualization)
# Usage: ./play.sh your-app.apk
# After READY, open http://localhost:6080 in a browser.
# From an iPhone on the same WiFi, open http://<SERVER-IP>:6080 instead.
set -e
cd "$(dirname "$0")"
APK="${1:-}"
if [ -z "$APK" ]; then echo "Usage: ./play.sh your-app.apk"; exit 1; fi
if [ ! -f "$APK" ]; then echo "APK not found: $APK"; exit 1; fi
command -v docker >/dev/null || { echo "Docker is required."; exit 1; }
docker compose up -d
echo "Waiting for emulator READY (this can take a few minutes on first boot)..."
for i in $(seq 1 60); do
  STATUS=$(docker exec android-container cat device_status 2>/dev/null || docker compose exec -T android cat device_status 2>/dev/null || echo "waiting")
  echo "status: $STATUS"
  if [ "$STATUS" = "READY" ]; then break; fi
  sleep 10
done
# Host adb: docker-android exposes adb on 5555
adb connect localhost:5555 || true
adb install -r "$APK"
echo "Installed. Open http://localhost:6080 in a browser and tap the app icon."
echo "iPhone on same WiFi: http://$(hostname -I | awk '{print $1}'):6080"
