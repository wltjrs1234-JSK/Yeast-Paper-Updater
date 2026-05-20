# S. cerevisiae Literature Auto-Updater

이 프로젝트는 매일 자동으로 S. cerevisiae(효모)와 관련된 최신 연구 문헌(논문, 프리프린트 등)을 검색하여 이메일로 전송해주는 파이프라인입니다.

**Europe PMC API**를 사용하여 PubMed뿐만 아니라 bioRxiv 등의 프리프린트 서버도 함께 검색합니다.

## 검색 카테고리
1. **Glutathione**: 효모 및 글루타티온 관련 최신 논문
2. **NMN**: 효모 및 NMN(Nicotinamide mononucleotide) 관련 논문
3. **Gene Editing Tools**: 효모 및 유전자 편집 기술(CRISPR, TALEN 등) 관련 논문

## 설정 및 실행 방법 (GitHub Actions 기반)

이 리포지토리를 포크(Fork)하거나 디렉터님의 GitHub 계정에 업로드한 뒤, 아래 설정을 진행해 주세요.

### 1. 이메일 발송용 앱 비밀번호 생성 (Naver 기준)
1. 네이버 메일 웹페이지에 접속하여 좌측 하단의 **환경설정** 아이콘을 클릭합니다.
2. **POP3/IMAP 설정** 탭으로 이동하여 **SMTP 사용**을 **사용함**으로 변경합니다.
3. 네이버 내정보 > 보안설정 > **2단계 인증**을 설정한 후, **애플리케이션 비밀번호 관리** 메뉴로 이동합니다.
4. 비밀번호 생성 용도를 입력하고(예: 'GitHub Actions') 생성된 애플리케이션 비밀번호를 복사해둡니다.

### 2. GitHub Secrets 설정
GitHub 리포지토리의 `Settings` > `Secrets and variables` > `Actions`로 이동하여 **New repository secret** 버튼을 눌러 다음 3가지 환경변수를 등록합니다.

- `EMAIL_SENDER`: 메일을 발송할 네이버 이메일 주소 (예: `myid@naver.com`)
- `EMAIL_PASSWORD`: 위 1단계에서 발급받은 네이버 애플리케이션 비밀번호
- `EMAIL_RECEIVER`: 메일을 수신받을 이메일 주소 (발송 이메일과 동일해도 무방합니다)

### 3. 수동 테스트
`Actions` 탭으로 이동하여 `S. cerevisiae Literature Daily Update` 워크플로우를 선택한 뒤, **Run workflow** 버튼을 눌러 스크립트가 정상적으로 실행되고 이메일이 수신되는지 확인합니다.

---
성공적으로 설정되었다면, 매일 오전 9시(한국시간 기준)에 지난 48시간 동안 새롭게 등록된 문헌들이 요약본(Abstract) 및 링크와 함께 이메일로 자동 전송됩니다.
