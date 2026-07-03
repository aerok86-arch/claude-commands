---
name: pe-intel
description: Pull today's PE intelligence digest — combining the daily pe-research briefing with pe-trendchaser signals, reframed for a PE deal professional. Use this skill whenever the user asks "what's happening in PE today?", "morning brief", "any deals I should know about?", "what did pe-research say today?", or opens Claude in the morning and seems to want a market update. Also trigger proactively if the user hasn't checked in and it's morning.
---

# pe-intel

오늘의 PE 인텔 다이제스트. pe-research 일일 브리핑 + pe-trendchaser 시그널을 통합해서 운용역 관점으로 재구성.

## 사용법

```
/pe-intel
```

인수 날짜 지정: `/pe-intel 2026-07-01`

---

## 실행 프롬프트

오늘($ARGUMENTS 없으면 오늘 날짜) 기준 PE 인텔 다이제스트를 생성함.

### 1. pe-research 일일 브리핑 조회

Notion DB `690d6d64-46dc-4f4f-a970-0543377139c2`에서 오늘 날짜 리포트 조회.
없으면 최근 1건 조회.

핵심 내용 추출:
- Deals & Transactions (글로벌 + 한국)
- Fundraising 동향
- 오늘의 Action Items

### 2. pe-trendchaser 시그널 조회

pe-trendchaser.vercel.app의 PE/VC/AI 탭에서 score ≥ 70 시그널 조회.
딜소싱 관련성 있는 시그널 최대 5건 선별.

### 3. 운용역 관점 재구성

아래 포맷으로 정리:

```
## 🔥 오늘 놓치면 안 되는 것 (TOP 3)
1. [딜/이벤트] — SV 관련성: [직접/간접/참고]
2. ...

## 💼 딜 & 트랜잭션
- 국내: ...
- 글로벌: ...

## 💰 펀드레이징
- ...

## 🎯 소싱 힌트
- pe-trendchaser 시그널 중 딜 소싱 가능성 있는 것:
  - [시그널] → [접근 방법]

## ✅ 오늘 할 일
- [ ] ...
```

### 4. 딜 연결

조회된 딜 중 Notion Deal Sheet에 없는 새 딜 → 추가 여부 확인 제안.

**출력 형식**: 음슴체. 3분 안에 읽을 수 있는 분량 (800자 이내).
