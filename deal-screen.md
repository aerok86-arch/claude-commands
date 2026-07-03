---
name: deal-screen
description: Run a Stage 1 PE deal screening on any company or deal. Use this skill whenever the user mentions a company name and wants to evaluate it as a potential investment target, asks "should we look at this?", "quick screen on X", "what do you think about X as a deal?", or pastes a deal memo and wants an initial read. Also trigger when the user mentions a company in a PE/M&A context and seems to want a go/no-go opinion. Works for Korean PE deals — uses DART, news, and SV Investment criteria.
---

# deal-screen

S1 빠른 딜 스크리닝. 회사명 또는 딜명을 받아 SV Investment 투자 기준으로 1차 적합성 판단.

## 사용법

```
/deal-screen [회사명 또는 딜명]
```

예시: `/deal-screen 아무개테크` / `/deal-screen 삼양식품 바이아웃`

---

## 실행 프롬프트

다음 절차로 $ARGUMENTS 에 대한 S1 스크리닝을 수행함:

### 1. 기본 정보 수집 (DART + NaverSearch)

- DART에서 최근 사업보고서 조회 → 매출, 영업이익, EBITDA(추정), 부채비율 확인
- NaverSearch로 최근 6개월 뉴스 검색 → 딜 관련 보도, 오너십 변동, 분쟁 여부 확인
- 확인 불가 수치는 반드시 `[미확인]` 태그 표시

### 2. SV 투자 기준 적합성 평가 (G1 적용)

아래 항목을 테이블로 정리:

| 기준 | 세부 내용 | 판단 | 출처 |
|------|----------|------|------|
| 매출 규모 | 연매출 [금액] | ✅/⚠️/❌ | |
| EBITDA 마진 | [%] | ✅/⚠️/❌ | |
| 경영권 인수 가능성 | 오너 구조, 지분 현황 | ✅/⚠️/❌ | |
| 섹터 적합성 | [섹터] — SV 관심 섹터 여부 | ✅/⚠️/❌ | |
| 차별화 포인트 | 시장 포지션, 진입장벽 | ✅/⚠️/❌ | |
| 리스크 신호 | 소송, 규제, 오너 리스크 | ✅/⚠️/❌ | |

### 3. 최종 판단 (4단계)

- **GO**: 2~3주 내 NDA + CIM 요청 권장
- **WATCH**: 6개월 후 재검토 조건 명시
- **COND**: 추가 확인 필요 항목 리스트업
- **NO-GO**: 핵심 이유 1~3줄

### 4. 다음 액션

- GO/COND 시: Notion Deal Sheet에 새 딜 추가 제안 (NOTION_DEAL_DB_ID)
- WATCH 시: 모니터링 일정 제안

**출력 형식**: 음슴체. G1 통과 기준(미확인 태그 3개 미만) 상단에 명시.
