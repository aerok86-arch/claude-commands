---
name: session-review
description: Run a loop engineering review at the end of a Claude session — analyzing what was done, surfacing skill candidates from repeated tasks, logging improvements, and writing a next-session starter. Use this skill whenever the user says "session review", "wrap up", "what should we turn into a skill?", or "log what we did." Also trigger automatically when the user signals they're done for the day or the session is winding down. This is the core self-improvement loop of the Agentic OS.
---

# session-review

루프 엔지니어링 스킬. 현재 세션에서 한 일을 분석해서 새 스킬 후보를 도출하고, 기존 스킬 개선점을 찾음.
세션 종료 전에 실행하는 습관이 Agentic OS를 자가 개선하는 핵심 루프임.

## 사용법

```
/session-review
```

---

## 실행 프롬프트

현재 세션 전체를 분석해서 루프 엔지니어링 리포트를 생성함.

### 1. 세션 요약

이번 세션에서 수행한 주요 작업을 나열:
- 실행한 스킬 목록과 결과
- 수동으로 반복한 작업 (스킬화 안 된 것)
- 발생한 에러 또는 막힌 지점

### 2. 스킬화 후보 발굴

이번 세션에서 2회 이상 반복하거나, 다음에도 똑같이 할 것 같은 작업:

| 반복 작업 | 빈도 | 스킬화 난이도 | 제안 명령어 |
|----------|------|-------------|-----------|
| | | 쉬움/보통/어려움 | |

### 3. 기존 스킬 개선점

이번 세션에서 사용한 스킬 중 불편했거나 결과가 기대에 못 미친 것:

| 스킬 | 문제점 | 개선 방향 |
|------|--------|----------|
| | | |

### 4. G1~G4 게이트 실패 로그

이번 세션에서 게이트 실패 또는 [미확인] 태그가 붙은 항목:
→ 다음 세션에서 해결할 TO-DO로 전환

### 5. Notion 실행 로그 기록

NOTION_MEETING_DB_ID에 세션 로그 페이지 생성:
- 제목: `세션 로그 · YYYY-MM-DD`
- 내용: 1~4번 요약
- 신규 스킬 후보 → Action Item 등록

### 6. 다음 세션 스타터

다음 세션 시작할 때 바로 쓸 수 있는 컨텍스트 요약 (3~5줄):
```
다음 세션 컨텍스트:
- 진행 중인 딜: ...
- 보류된 작업: ...
- 신규 스킬 작업 예정: ...
```

**출력 형식**: 음슴체. 실행 시간 5분 이내로 완료.
