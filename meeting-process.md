---
name: meeting-process
description: Convert raw meeting notes or STT transcripts into a structured memo with action items, then save to Notion. Use this skill whenever the user pastes meeting notes, a transcript, or says "process this meeting", "turn this into a memo", "I just had a call with X", or "save this to Notion." Also trigger when the user shares unstructured notes after a deal meeting, LP meeting, or portfolio review and wants them cleaned up. Works with both Korean and English input.
---

# meeting-process

회의록 → 구조화 메모 + 액션 아이템 → Notion 자동 저장.
meeting-pipeline에서 STT 처리된 텍스트 또는 직접 붙여넣은 메모 모두 처리 가능.

## 사용법

```
/meeting-process
```

실행 후 Claude가 회의 정보를 질문함. 또는 호출 시 바로 텍스트 붙여넣기 가능.

---

## 실행 프롬프트

사용자에게 순서대로 확인:
1. 회의 날짜 및 참석자 (회사명 포함)
2. 회의 목적 (딜미팅 / 포트폴리오 리뷰 / LP 미팅 / 기타)
3. 회의록 원문 (STT 텍스트 또는 메모 붙여넣기 요청)

입력받은 내용을 아래 구조로 변환:

### 출력 구조

```
# 미팅 메모 — [회사명] | [날짜]

## 기본 정보
- 일시: YYYY-MM-DD
- 참석자: [내부] 운용역 / [외부] 이름(직책, 회사)
- 목적: [딜미팅 S1 / 포트폴리오 리뷰 / LP 미팅 / 기타]

## 핵심 논의 사항
1. [주제] — [내용 요약]
2. ...

## 딜/투자 관련 수치
| 항목 | 수치 | 출처/확인 |
|------|------|----------|
| 매출 | | |
| EBITDA | | |
| 밸류에이션 | | |

## 상대방 포지션 & 우리 포지션
- 상대방: ...
- 우리: ...

## 합의된 사항
- ...

## 액션 아이템
- [ ] [담당자] [기한] — [할 일]
- [ ] ...

## 다음 미팅
- 예정일: ...
- 의제: ...
```

### Notion 저장

정리된 메모를 NOTION_MEETING_DB_ID에 새 페이지로 생성.
딜 관련 미팅이면 NOTION_DEAL_DB_ID의 해당 딜 페이지에 relation 연결 시도.

### People DB 연결

참석자가 notion-obsidian-sync의 People DB에 있으면 자동 mention 제안.

**출력 형식**: 음슴체. 확인 불가 수치는 `[미확인]` 태그.
