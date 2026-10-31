# APK Cloud LITE - 똥컴만으로, 연결 없이, 로컬 가상 태블릿

준비물: 똥컴 끝. 실제 안드로이드 태블릿 필요 없음. 폰 필요 없음. 별도 서버 필요 없음.

이 레포는 GitHub Pages가 안드로이드를 돌리는 게 아니다.
GitHub의 역할은 코드 보관과 안내 페이지(index.html) 제공뿐이다.
실제 안드로이드는 똥컴에 설치하는 PC 프로그램이 돌린다. 블루스택과 같은 방식이다.
HTML 웹사이트 안에 안드로이드 OS를 담아서 무거운 3D 게임을 돌리는 것은 현재 웹 기술로 안 된다.

## 기본 구조 (똥컴 모드, 연결 없음)

- `index.html` - 똥컴 모드 안내 페이지. 서버 연결 입력이 없다.
- `pc-lite/README-LITE.md` - 똥컴 모드 설명
- `pc-lite/setup-lite.bat` - Android 10 경량 태블릿 기기(lite, Nexus 10, 1280x800, RAM 1024MB) 설치
- `pc-lite/play-lite.bat` - 플레이어 실행
- `pc-lite/lite-player.py` - Tkinter 플레이어. 에뮬레이터 시작, APK 설치, 실행, scrcpy 화면(720p 제한), Roblox 공식 PC 클라이언트 실행
- `pc-lite/lite-check.py` - RAM, CPU, 디스크, 도구 확인

## 똥컴에서 실행

1. `pc-lite` 폴더를 똥컴에 복사한다.
2. `python lite-check.py`
3. 구글 공식 Command line tools zip을 받아 같은 폴더에 넣고 `setup-lite.bat`을 실행한다.
4. `play-lite.bat`을 실행한다.

## 별도 서버가 있는 경우에만 (옵션)

- `docker/docker-compose.yml` - budtmo/docker-android, noVNC 6080, adb 5555
- `docker/play.sh` - 부팅 대기 + adb 설치
- `server/player.py`, `server/panel.html` - 예전에 만든 Windows 로컬 패널 코드 (참고용)

이 옵션은 똥컴 모드의 기본이 아니다. noVNC를 인터넷에 그대로 공개하지 마라.

## 한계 (솔직히)

- GitHub Pages, GitHub Actions로는 24시간 게임용 안드로이드 서버를 돌릴 수 없다. Actions로 오래 돌리면 계정이 막힐 수 있다.
- 구조 변경은 Docker, KVM, 서버 연결이라는 무게를 뺀 것이다. 똥컴에 GPU와 RAM이 생기는 게 아니다.
- 가벼운 2D APK와 Roblox PC 클라이언트는 될 가능성이 높다. 브롤 같은 무거운 3D 게임을 에뮬레이터로 고그래픽, 고프레임으로 돌리는 것은 하드웨어 한계로 보장할 수 없다.
- 가상 태블릿은 공식 에뮬레이터 태블릿 기기 정의를 쓴다. 앱 서버를 속이는 가짜 기기 정보 조작은 하지 않는다.
- 출처를 모르는 APK는 설치하지 마라. 공식 스토어가 아닌 APK는 악성코드와 계정 정지 위험이 있다.
