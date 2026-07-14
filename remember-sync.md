---
description: 리멤버(rememberapp.co.kr) 개인명함첩 export를 다운로드해서 Notion 👥 People DB에 신규 인력만 동기화 (옛 연락처 DB는 2026-07-14 삭제됨)
argument-hint: (인자 없음 — 그냥 /remember-sync)
allowed-tools: Bash, Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__find, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__tabs_create_mcp, mcp__Zapier-MCP__execute_zapier_read_action, mcp__Zapier-MCP__list_enabled_zapier_actions
---

# /remember-sync — 리멤버 명함 → Notion 연락처 동기화

aerok86@gmail.com에 리멤버(no-reply@rememberapp.co.kr)의 "[remember] 명함 파일 생성이 완료되었습니다." 메일이 오면, 그 안의 다운로드 파일을 받아서 `~/notion-obsidian-sync/remember_sync.py`로 Notion "👥 People" DB(Life Hub 내 유일한 관계 자산 DB — 옛 "연락처" DB는 2026-07-14 삭제됨)에 **명함등록일 기준 신규분만, 전화번호가 이미 People에 있으면 스킵**하며 반영하는 스킬. 매 실행 확인 없이 바로 진행하되(자율 진행 선호), **Notion에 실제로 쓰기 직전에는 몇 건이 신규인지 요약해서 한 번 보여주고 진행**(대량 write라 되돌리기 번거로움).

## Step 1. 최근 "명함 파일 생성 완료" 메일 확인

Gmail에서 `from:no-reply@rememberapp.co.kr subject:"명함 파일 생성이 완료되었습니다"`로 검색해 가장 최근 메일을 찾음. 본문에 "요청 일시"와 "선택한 명함: N개"가 있음 — 이게 이번에 받을 파일의 스냅샷 정보.

`~/notion-obsidian-sync/remember_sync_state.json`의 `last_run`과 비교해서, 이 메일의 요청 일시가 이미 처리된 것보다 새로운지 확인. 새 게 없으면 "동기화할 신규 메일 없음"으로 종료.

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

출력에 체크포인트(마지막 동기화된 명함등록일), 신규 대상 건수, 신규 인원 미리보기(최대 20명)가 나옴. **이 결과를 사용자에게 한 번 보여주고 진행 여부 확인** (몇 명 신규인지가 매번 다르므로, 특히 처음 실행이라 체크포인트를 새로 계산하는 경우 숫자가 클 수 있음).

## Step 4. 실제 반영

승인되면:
```bash
python3 ~/notion-obsidian-sync/remember_sync.py "~/Downloads/개인명함첩_<받은파일명>.xlsx" --apply
```

완료 후 `remember_sync_state.json`의 체크포인트가 자동 갱신됨(다음 실행부터는 이번에 처리된 최신 명함등록일 이후만 신규로 잡음).

## 필드 매핑 (참고 — 코드에 이미 반영됨)

People DB에는 부서/회사폰/팩스/명함첩 이름/그룹 전용 필드가 없어 `Notes`에 묶어서 텍스트로 보존한다.

| 리멤버 xlsx 컬럼 | Notion People 속성 |
|---|---|
| 이름 | Name (title) |
| 회사 | 회사명 |
| 직함 | Role |
| 전자 메일 주소 | Company email |
| 휴대폰 | Phone |
| 근무지 주소 | Location |
| 명함 등록일 | 명함등록일 (date, "YYYY년 MM월 DD일" 원문을 ISO 날짜로 파싱해 저장) |
| (고정값) | Category = "업무" |
| 부서, 근무처 전화, 근무처 팩스, 명함첩 이름, 그룹, 메모 | Notes 한 필드에 묶어서 보존 |

## 알아둘 것

- `remember_sync.py`는 표준 라이브러리만 사용(xlsx도 zipfile+xml로 직접 파싱, openpyxl 등 외부 의존성 없음) — `~/notion-obsidian-sync/.env`의 `NOTION_TOKEN` 재사용(People DB 동기화와 같은 통합).
- 체크포인트는 "명함등록일"(리멤버 원본 필드) 기준. 최초 실행 시(체크포인트 파일 없을 때만) People DB 전체를 스캔해 현재 최댓값을 로컬 상태 파일에 시드해둠.
- People DB는 이미 4천명 이상이 등록된 curated 관계 자산 DB라, `--apply` 시 생성 직전에 People 전체 전화번호를 한 번 더 스캔해서 **동일 전화번호가 이미 있으면 새 페이지를 만들지 않고 스킵**한다(중복 인물 생성 방지).
- 리멤버 xlsx는 매번 전체 명함첩을 통째로 내보내는 방식(증분 아님) — 그래서 매번 전체를 다시 파싱하되 체크포인트 이후분만 필터링하는 구조로 안전하게 idempotent.
- 개인정보(전화번호·이메일 등)를 다루므로 dry-run 없이 바로 `--apply` 하지 말 것.
- 2026-07-14: 옛 "연락처" DB(비즈니스 명함 raw DB)가 사용자에 의해 완전 삭제되어, 이후로는 People DB가 유일한 동기화 대상이다.
