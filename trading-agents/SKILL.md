---
name: trading-agents
description: Multi-agent equity research and buy/sell/hold simulation modeled on TauricResearch/TradingAgents. Runs an Analyst Team (fundamentals, sentiment, news, technical) into a Bull-vs-Bear Researcher debate, a Trader plan, a Risky/Neutral/Safe risk debate, and a final Fund Manager verdict. Covers both US/global stocks (FMP, yfinance via PlayMCP, web search) and Korean KOSPI/KOSDAQ stocks (DART filings via opendart, Naver news/blog/cafe search, Naver Finance, YouTube sentiment). Use when the user asks to analyze a stock, wants a buy/sell/hold call, says "이 종목 분석해줘", "매수해도 될까", "TradingAgents 스타일로 봐줘", "종목 리서치 해줘", "이 주식 어때", or names a ticker/company and wants an investment view. Output is a simulated research debate, not financial advice.
---

# TradingAgents (한국 주식 지원판)

TauricResearch의 [TradingAgents](https://github.com/TauricResearch/TradingAgents) 멀티에이전트 트레이딩 프레임워크를 하나의 Claude 대화 안에서 재현한다. 실제 트레이딩 데스크처럼 여러 역할(애널리스트 → 리서처 → 트레이더 → 리스크팀 → 펀드매니저)이 순서대로 데이터를 수집·토론한 뒤 최종 투자 판단을 낸다.

원본은 역할마다 별도 LLM 에이전트(LangGraph)를 띄우지만, 이 스킬은 **같은 대화 안에서 역할을 순차 전환하며 실제 도구 호출로 데이터를 채워 토론을 진행**한다. 매 단계는 반드시 실제 조회한 데이터에 근거해야 하고, 추측이나 학습된 지식만으로 채우지 않는다.

## 0단계 — 종목 식별 & 시장 분류

사용자가 말한 종목을 확정하고 시장을 분류한다.

- **한국 상장사** (KOSPI/KOSDAQ, 6자리 코드 또는 한글 종목명) → `references/kr-data-sources.md`의 소스 사용
- **미국/글로벌 상장사** (티커) → `references/global-data-sources.md`의 소스 사용

회사명만 주어졌다면 한국은 `opendart-find_company`, 해외는 `FMP search`로 정식 티커/고유번호부터 확정한다. 동명이인·동명회사 등 모호하면 사용자에게 확인 후 진행한다(단, 상장사가 1곳뿐이면 바로 진행).

## 워크플로우 (5단계)

각 단계 시작 전에 `references/agent-personas.md`에서 해당 역할의 상세 지침·톤·체크리스트를 확인한다. 최종 응답에는 5단계를 모두 포함하고 소제목으로 구분한다. 대화 흐름을 위해 각 단계는 간결하게(3~8줄) 쓰되, 근거 데이터는 구체적 수치로 제시한다.

### 1단계 — 애널리스트 팀 (병렬 데이터 수집)
4개 역할이 각각 실제 도구로 데이터를 조회하고 요약을 작성한다.
1. **Fundamentals Analyst** — 재무·밸류에이션 (매출/이익 추이, 마진, 부채비율, PER/PBR 등)
2. **Sentiment Analyst** — 뉴스·커뮤니티·유튜브 심리 (긍정/부정 톤, 화제성 변화)
3. **News Analyst** — 거시/업종 뉴스, 공시, 촉매 이벤트 (실적발표일, 신제품, 규제 등)
4. **Technical Analyst** — 가격 추세, 거래량, 주요 기술적 지표, 지지/저항

### 2단계 — 리서치 팀 토론 (Bull vs Bear)
1단계 데이터를 근거로 Bull Researcher가 강세론을, Bear Researcher가 약세론을 제시하고 서로 1회씩 반박(rebuttal)한다. 마지막에 Research Manager가 어느 쪽 논거가 더 강한지, 어떤 조건에서 판이 뒤집히는지 판정한다.

### 3단계 — 트레이더
리서치 토론 결과를 바탕으로 구체적 매매 계획 초안을 작성한다: 방향(매수/매도/관망), 목표가, 진입 구간, 손절가, 투자 기간.

### 4단계 — 리스크 관리 팀 토론
공격적(Risky) / 중립적(Neutral) / 보수적(Safe) 3개 리스크 페르소나가 트레이더 계획을 각자의 시각에서 비판적으로 검토한다. Risk Manager가 최종 조정안을 낸다.

### 5단계 — 펀드매니저 최종 판단
`references/output-template.md` 형식으로 최종 리포트를 작성한다: 최종 판단(BUY/HOLD/SELL), 확신도, 핵심 논지 한 줄, 근거 요약, 리스크와 무효화 조건(어떤 일이 생기면 판단을 재검토해야 하는지), 참고 출처.

## 중요 원칙
- 매 단계는 실제 도구 호출 결과에 근거한다. 확인 안 된 수치는 `[미확인]`으로 표시하고 지어내지 않는다.
- 한국 종목은 DART 공시(opendart)가 가장 신뢰도 높은 소스다 — 최신 사업/분기보고서를 우선한다.
- 유튜브·커뮤니티 심리는 보조 지표일 뿐, 단독 근거로 최종 판단을 내리지 않는다.
- 최종 출력 맨 위에 "투자 조언이 아닌 시뮬레이션된 리서치 토론입니다" 고지를 포함한다.
- 데이터 출처(공시, 기사, 영상 링크)를 각주/링크로 남겨 사용자가 직접 검증할 수 있게 한다.
- 대상 종목이 무엇이든(한국/해외 불문) 동일한 5단계 구조를 유지해 일관된 형식으로 비교 가능하게 한다.

## Native Upstream
Inspired by TauricResearch/TradingAgents: https://github.com/TauricResearch/TradingAgents (multi-agent LLM trading framework — Analyst/Researcher/Trader/Risk Management/Fund Manager role structure). This skill reimplements that role structure as a single-conversation, tool-augmented workflow inside Claude, extended with Korean market coverage (DART filings, Naver search, Naver Finance, YouTube sentiment) that the original framework (built on yfinance/Finnhub/Reddit) does not cover.
