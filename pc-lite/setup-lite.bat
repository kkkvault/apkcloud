@echo off
chcp 65001 >nul
cd /d %~dp0
echo APK Cloud - PC LITE setup (low-spec PC only, no Docker, no server)
echo This PC only. No cloud, no Docker, no KVM needed for this route.
echo.
where python >nul 2>&1
if errorlevel 1 echo Python not found. Install Python 3 and tick Add to PATH, then run again. & pause & exit /b 1
where java >nul 2>&1
if not errorlevel 1 goto JAVA_OK
echo Java not found. Trying winget install Microsoft.OpenJDK.17 ...
winget install --id Microsoft.OpenJDK.17 -e --accept-source-agreements --accept-package-agreements
where java >nul 2>&1
if errorlevel 1 echo Still no Java. Install Temurin 17 JDK manually, add java to PATH, then run again. & pause & exit /b 1
:JAVA_OK
if exist sdk\cmdline-tools\latest\bin\sdkmanager.bat goto INSTALL_PKGS
set ZIPFILE=
for %%F in (commandlinetools-win-*.zip) do set ZIPFILE=%%F
if "%ZIPFILE%"=="" goto NEED_ZIP
echo Found %ZIPFILE% - extracting...
powershell -Command "Expand-Archive -Force '%ZIPFILE%' -DestinationPath '%~dp0tmpcmd'"
mkdir sdk\cmdline-tools 2>nul
move "%~dp0tmpcmd\cmdline-tools" "%~dp0sdk\cmdline-tools\latest"
rmdir /s /q "%~dp0tmpcmd"
if not exist sdk\cmdline-tools\latest\bin\sdkmanager.bat echo Extract failed. Check the zip layout. & pause & exit /b 1
:INSTALL_PKGS
set SDKDIR=%~dp0sdk
set PATH=%SDKDIR%\cmdline-tools\latest\bin;%SDKDIR%\platform-tools;%SDKDIR%\emulator;%PATH%
echo Installing LITE SDK packages (Android 10, x86, smaller than Android 14)...
call sdkmanager.bat "platform-tools" "platforms;android-29" "emulator" "system-images;android-29;google_apis;x86"
if not exist "%USERPROFILE%\.android\avd\lite.avd" echo no | call avdmanager.bat create avd -n lite -k "system-images;android-29;google_apis;x86" --device "Nexus 10"
echo Tuning lite tablet AVD for low-spec PC (1024MB RAM, 1280x800, 2 cores)...
powershell -Command "$p=\"$env:USERPROFILE\.android\avd\lite.avd\config.ini\"; if (Test-Path $p) { $t=Get-Content $p; $t=$t -replace 'hw.ramSize=.*','hw.ramSize=1024'; $t=$t -replace 'vm.heapSize=.*','vm.heapSize=256'; $t=$t -replace 'hw.cpu.ncore=.*','hw.cpu.ncore=2'; $t=$t -replace 'hw.lcd.width=.*','hw.lcd.width=1280'; $t=$t -replace 'hw.lcd.height=.*','hw.lcd.height=800'; $t=$t -replace 'hw.lcd.density=.*','hw.lcd.density=240'; $t=$t -replace 'disk.dataPartition.size=.*','disk.dataPartition.size=1024M'; $t | Set-Content $p }"
where scrcpy >nul 2>&1
if errorlevel 1 winget install --id Genymobile.scrcpy -e --accept-source-agreements --accept-package-agreements
echo.
echo DONE - LITE.
echo Next: run play-lite.bat. Start lite emulator, wait for home, then Choose APK, Install, Launch.
echo Roblox: use the Roblox PC button in the player - it runs the official Windows client, no emulator needed.
pause
exit /b 0
:NEED_ZIP
echo.
echo DOWNLOAD NEEDED (one time, official Google file only):
echo 1. Open developer.android.com/studio
echo 2. Scroll to Command line tools only, download the Windows zip.
echo 3. Put that zip file in this same folder (next to this bat file).
echo 4. Run setup-lite.bat again.
pause
exit /b 1
