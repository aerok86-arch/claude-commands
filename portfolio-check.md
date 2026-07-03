---
name: portfolio-check
description: Run a Stage 8 monitoring check on a portfolio company — pulling recent financials from DART, news, KPI vs investment thesis, value creation progress, and exit readiness. Use this skill whenever the user asks to "check on [company]", "what's the status of [portfolio company]?", "board prep for [company]", or "how is [company] doing?" Also trigger before board meetings, monthly reviews, or any time the user mentions a portfolio company name in a monitoring context.
---

# portfolio-check

포트폴리오 기업 현황 점검. 이사회/월간 리뷰 전 빠른 상태 확인.

## 사용법

```
/portfolio-check [회사명]
```

예시: `/portfolio-check 가나다` / `/portfolio-check 모든` (전체 포트폴리오)

---

## 실행 프롬프트

$ARGUMENTS 포트폴리오 기업에 대해 S8 모니터링 관점의 현황 점검 수행.

### 1. 기본 현황 (DART)

- 최근 분기 실적 (매출, 영업이익, 순이익)
- 최근 공시 (CB·BW·담보제공·소송·임원 변경 등)
- 재무 건전성: 부채비율, 이자보상배율

### 2. 뉴스 모니터링 (NaverSearch)

- 최근 3개월 주요 뉴스
- 업계 트렌드 관련 언급
- 경쟁사 동향

### 3. KPI vs 투자 thesis

Notion Deal Sheet에서 투자 당시 thesis 및 목표 KPI 조회.
현재 수치와 비교 → GAP 분석:

| KPI | 투자 시 목표 | 현재 | GAP | 판단 |
|-----|------------|------|-----|------|
| 매출 성장률 | | | | |
| EBITDA 마진 | | | | |
| 핵심 오퍼레이션 KPI | | | | |

### 4. Value Creation 진행 상황

S7 VCP에서 설정된 이니셔티브 진행 현황:
- On Track ✅ / At Risk ⚠️ / Off Track ❌ 판단

### 5. Exit 준비도

- 현재 EV/EBITDA 멀티플 (FMP 또는 DART 기반 컴프 적용)
- 예상 엑싯 타임라인
- Equity Story 현재 상태

### 6. 이사회 준비 사항

다음 이사회/리뷰 전 챙겨야 할 사항 3가지 이내.

**출력 형식**: 음슴체. 2페이지(A4) 분량. 수치는 출처 명시.
