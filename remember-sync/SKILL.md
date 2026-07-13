---
name: remember-sync
description: 리멤버(rememberapp.co.kr) 개인명함첩을 Notion "연락처" DB(👥 People과는 별도의 비즈니스 명함 raw DB)에 동기화한다. 리멤버 웹은 이메일 첨부가 아니라 웹 화면에서만 xlsx를 내보내므로, Gmail로 새 export가 생겼는지 확인한 뒤 브라우저 자동화로 card.rememberapp.co.kr에서 파일을 직접 다운로드하고, 명함등록일 체크포인트 기준 신규 인력만 Notion에 반영한다. Use when the user asks to sync Remember business cards to Notion, or says "리멤버 동기화", "명함 동기화해줘", "리멤버 연락처 업데이트", "remember sync", "명함첩 노션에 반영해줘".
allowed-tools:
  - Bash
  - Read
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__computer
  - mcp__claude-in-chrome__find
  - mcp__claude-in-chrome__get_page_text
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude_ai_Gmail__search_threads
  - mcp__claude_ai_Gmail__get_thread
---

# remember-sync — 리멤버 명함 → Notion 연락처 동기화

aerok86@gmail.com에 리멤버(no-reply@rememberapp.co.kr)의 "[remember] 명함 파일 생성이 완료되었습니다." 메일이 오면, 그 안에서 안내하는 파일을 받아 `~/notion-obsidian-sync/remember_sync.py`로 Notion "연락처" DB(👥 People과 별도, Life Hub 내 비즈니스 명함 raw DB)에 **명함등록일 기준 신규분만** 반영한다.

중요: 리멤버 메일에는 **엑셀 파일이 첨부되어 있지 않다.** 메일 본문의 "파일 다운로드하기" 링크는 로그인된 웹 화면으로 연결될 뿐이라, 실제 파일은 반드시 브라우저로 `card.rememberapp.co.kr`에 들어가 다운로드해야 한다. 메일은 "새 export가 생성됐는지, 몇 건짜리인지" 확인하는 트리거/메타데이터 용도로만 쓴다.

매 실행 확인 없이 바로 진행하되(자율 진행 선호), **Notion에 실제로 쓰기 직전에는 몇 건이 신규인지 요약해서 한 번 보여주고 진행**한다(대량 write라 되돌리기 번거로움).

## Step 1. 최근 "명함 파일 생성 완료" 메일 확인

Gmail에서 `from:no-reply@rememberapp.co.kr subject:"명함 파일 생성이 완료되었습니다"`로 검색해 가장 최근 메일을 찾는다. 본문에 "요청 일시"와 "선택한 명함: N개"가 있다 — 이게 이번에 받을 파일의 스냅샷 정보.

`~/notion-obsidian-sync/remember_sync_state.json`의 `last_run`과 비교해서, 이 메일의 요청 일시가 이미 처리된 것보다 새로운지 확인한다. 새 게 없으면 "동기화할 신규 메일 없음"으로 종료한다.

## Step 2. 브라우저로 파일 다운로드

`claude-in-chrome` 도구로 (사용자는 이미 리멤버 웹에 로그인되어 있음, 재로그인 불필요):

1. `card.rememberapp.co.kr/book/groups` 이동
2. "N개의 내보낸 명함 파일을 관리 중입니다" 배너의 "보러가기" 클릭 (또는 명함관리 화면에서 직접 파일 관리 진입)
3. "내보낸 파일 관리" 모달에서 최신 파일의 다운로드 버튼 클릭 (`find` 도구로 정확한 버튼 ref 찾아서 클릭 — 파일명이 `개인명함첩_YYMMDDHHMMSS.xlsx` 형식)
4. 다운로드가 `~/Downloads/`에 실제로 떨어졌는지 확인(`ls -lat ~/Downloads/*.xlsx`). 안 떨어지면: 스크린샷으로 네이티브 저장 다이얼로그가 떴는지 확인 후 저장 진행, 그래도 안 되면 사용자에게 상황 설명하고 직접 다운로드 요청.

## Step 3. dry-run으로 신규 건수 확인

```bash
python3 ~/notion-obsidian-sync/remember_sync.py "~/Downloads/개인명함첩_<받은파일명>.xlsx"
```

출력에 체크포인트(마지막 동기화된 명함등록일), 신규 대상 건수, 신규 인원 미리보기(최대 20명)가 나온다. **이 결과를 사용자에게 한 번 보여주고 진행 여부 확인**한다(몇 명 신규인지가 매번 다르므로, 특히 처음 실행이라 체크포인트를 새로 계산하는 경우 숫자가 클 수 있음).

## Step 4. 실제 반영

승인되면:

```bash
python3 ~/notion-obsidian-sync/remember_sync.py "~/Downloads/개인명함첩_<받은파일명>.xlsx" --apply
```

완료 후 `remember_sync_state.json`의 체크포인트가 자동 갱신된다(다음 실행부터는 이번에 처리된 최신 명함등록일 이후만 신규로 잡음).

## 필드 매핑 (참고 — 코드에 이미 반영됨)

| 리멤버 xlsx 컬럼 | Notion 연락처 속성 |
|---|---|
| 이름 | 이름 (title) |
| 회사 | 회사 |
| 부서 | 부서 |
| 직함 | 직책 |
| 전자 메일 주소 | 이메일 주소 |
| 근무처 전화 | 회사폰 |
| 근무처 팩스 | 팩스 |
| 휴대폰 | 스마트폰 |
| 명함 등록일 | 등록일 (rich_text, "YYYY년 MM월 DD일" 원문 그대로) |
| 그룹 (콤마 구분) | 그룹 (multi_select) |
| 메모 | 관계 및 특성 |
| 근무지 주소, 명함첩 이름 | 매핑 안 함 (Notion 쪽에 대응 필드 없음) |

## 알아둘 것

- `remember_sync.py`는 표준 라이브러리만 사용(xlsx도 zipfile+xml로 직접 파싱, openpyxl 등 외부 의존성 없음) — `~/notion-obsidian-sync/.env`의 `NOTION_TOKEN` 재사용(People DB 동기화와 같은 통합).
- 체크포인트는 "명함등록일"(리멤버 원본 필드) 기준. Notion의 `등록일`이 date 타입이 아니라 rich_text라 Notion API 서버사이드 정렬이 안 먹어서, 최초 실행 시 연락처 DB 전체를 스캔해 현재 최댓값을 로컬 상태 파일에 시드해둔다.
- 리멤버 xlsx는 매번 전체 명함첩을 통째로 내보내는 방식(증분 아님) — 그래서 매번 전체를 다시 파싱하되 체크포인트 이후분만 필터링하는 구조로 안전하게 idempotent하다.
- 개인정보(전화번호·이메일 등)를 다루므로 dry-run 없이 바로 `--apply` 하지 말 것.
- 실행 스크립트와 체크포인트 상태 파일(`remember_sync_state.json`)은 `~/notion-obsidian-sync/`에 상주한다(다른 Notion↔Obsidian 동기화 스크립트와 `.env`를 공유하기 위함). 이 폴더의 `remember_sync.py`가 실제 실행되는 원본이고, `scripts/remember_sync.py`는 repo 배포용 사본이다 — 로직을 고치면 두 곳 모두 수동으로 반영해야 한다(동기화 자동화 없음).

## Native Upstream
없음 — 사용자 개인 워크플로용으로 처음부터 작성된 스킬(외부 프레임워크 재구현이 아님).
