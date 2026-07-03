---
name: ic-prep
description: Prepare a full Investment Committee memo package for a PE deal. Use this skill whenever the user mentions a deal and wants to prepare for IC, asks for an "IC memo", "investment committee prep", "IC checklist", or says "we're going to IC on this deal." Also trigger when the user is moving a deal from Due Diligence to IC stage and needs a structured output. Applies G1–G4 quality gates and generates expected IC questions with draft answers.
---

# ic-prep

S5 IC 메모 준비. 딜명을 받아 IC 발표 구조, 체크리스트, 예상 질문을 생성.

## 사용법

```
/ic-prep [딜명]
```

예시: `/ic-prep 아무개테크 바이아웃` / `/ic-prep 가나다 경영권 인수`

---

## 실행 프롬프트

$ARGUMENTS 에 대한 IC 발표 준비 패키지를 생성함. G1~G4 전체 게이트 적용.

### 1. Notion Deal Sheet 조회

NOTION_DEAL_DB_ID에서 해당 딜의 현재 스테이지, 기록된 수치, 메모 확인.
없으면 사용자에게 핵심 수치(매출, EBITDA, EV, 지분율)를 요청.

### 2. IC 메모 구조 (G4 필수 섹션)

```
## 1. 투자 기회 요약 (Executive Summary)
   - 딜 개요 3줄
   - 투자 thesis 핵심

## 2. 시장 기회 (G4 ✅)
   - TAM / SAM 추정 [출처 필수]
   - 시장 성장률 및 드라이버
   - 경쟁 구도

## 3. 기업 분석
   - 사업 모델 & 수익구조
   - 핵심 경쟁우위
   - 경영진 평가

## 4. 재무 분석 (G4 ✅)
   - 최근 3년 실적 요약 [출처: DART]
   - EBITDA 정상화 조정 항목
   - 핵심 재무 비율

## 5. 밸류에이션 (G1 ✅)
   - EV/EBITDA 멀티플 근거 [출처 필수]
   - LBO 수익률 민감도 (Base / Bull / Bear)
   - 컴프 트랜잭션 [미확인 시 태그]

## 6. 리스크 & 완화 방안 (G4 ✅)
   - Top 3~5 리스크
   - 각 리스크별 완화 전략
   - 다운사이드 시나리오

## 7. 투자 의견 & 조건 (G4 ✅)
   - 투자 권고 (GO / COND / NO-GO)
   - 승인 조건 (있다면)
   - 다음 단계
```

### 3. IC 발표 전 체크리스트

- [ ] G1: [미확인] 태그 3개 미만 확인
- [ ] G2: 모든 수치에 [출처: ...] 태그
- [ ] G3: 컴프 트랜잭션 외부 검증 (DART/FMP)
- [ ] G4: 4대 필수 섹션(시장기회·재무·리스크·투자의견) 완결
- [ ] 경쟁 펀드 동향 확인 (동일 딜 관심 여부)
- [ ] 법률/세무 쟁점 사전 검토 여부

### 4. 예상 IC 질문 10선

IC 위원들이 던질 가능성 높은 질문을 업종 + 딜 구조 기반으로 생성.
각 질문에 답변 초안 포함.

**출력 형식**: 음슴체. G1~G4 게이트 상태를 맨 위에 배지로 표시.
