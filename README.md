# 내 클라우드 안드로이드 (GitHub로 직접 만드는 서버)

이 레포는 GitHub Pages가 안드로이드를 돌리는 게 아니다.
GitHub의 역할은 코드 보관과 연결판(index.html) 제공뿐이다.
실제 안드로이드는 네가 직접 돌리는 서버에서 돌아간다.

## 구조

- `index.html` - 내 서버 주소 입력 + 새 탭 연결판. 주소는 브라우저 localStorage에만 저장된다.
- `docker/docker-compose.yml` - budtmo/docker-android, noVNC 6080, adb 5555
- `docker/play.sh` - 부팅 대기 + adb 설치
- `server/player.py`, `server/panel.html` - 예전에 만든 Windows 로컬 패널 코드 (참고용)

## 서버에서 실행

1. 서버에 `docker/` 폴더를 복사한다.
2. `docker compose up -d`
3. 부팅이 끝날 때까지 기다린다.
4. `./play.sh 파일.apk`
5. 브라우저에서 `http://서버IP:6080` 으로 들어간다.

## 한계 (솔직히)

- GitHub Pages, GitHub Actions로는 24시간 게임용 안드로이드 서버를 돌릴 수 없다. Actions로 오래 돌리면 계정이 막힐 수 있다.
- 똥컴만으로는 무거운 3D 게임용 에뮬레이터를 돌리기 어렵다. 서버에는 Docker와 /dev/kvm이 필요하다.
- 서버가 꺼지면 화면도 멈춘다.
- noVNC를 인터넷에 그대로 공개하지 마라. 집 와이파이 안에서만 쓰거나 Tailscale 같은 사설 네트워크 안에서만 열어라.
- 출처를 모르는 APK는 설치하지 마라. 공식 스토어가 아닌 APK는 악성코드와 계정 정지 위험이 있다.
