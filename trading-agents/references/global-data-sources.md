# 미국/글로벌 종목 데이터 소스 플레이북

TradingAgents 원본이 커버하던 영역과 동일한 데이터를 이 세션에 연결된 도구로 재현한다.

## 0. 종목 확정

- `mcp__claude_ai_FMP__search` — 회사명 → 정식 티커 확정.

## 1. Fundamentals

- `FMP company` — 프로필(업종, 시가총액, 개요)
- `FMP statements` — 손익계산서/재무상태표/현금흐름표 (최근 3개 분기·연도 비교)
- `FMP discountedCashFlow` — DCF 기반 내재가치 참고치
- `FMP analyst` — 애널리스트 컨센서스(목표주가, 투자의견)
- `FMP secFilings` — 10-K/10-Q/8-K 등 공시
- `PlayMCP UsStockInfo-get_financial_statement`, `get_stock_info` — 보조/교차검증용(yfinance 기반)

## 2. News / Catalysts

- `FMP news` — 종목/업종 뉴스
- `FMP calendar` — 실적발표일 등 예정 이벤트
- `PlayMCP UsStockInfo-get_finance_news` — 보조 뉴스 소스
- `WebSearch` — FMP에 없는 최신 이슈, 업종 전반 동향

## 3. Sentiment

- `FMP news`의 헤드라인 톤 종합
- `WebSearch`로 Reddit/StockTwits/유튜브 심리 확인: `"<티커> stock reddit"`, `"<티커> stock price target site:youtube.com"` 등. 개별 영상 스크립트가 필요하면 `WebFetch`로 영상 페이지(설명·상단 댓글)를 읽는다.
- `FMP senate` — 미 의회 의원 매매 내역(있으면 참고 신호로만 사용)

## 4. Technical

- `FMP technicalIndicators` — RSI/MACD/이동평균 등 정량 지표
- `PlayMCP UsStockInfo-get_historical_stock_prices` — 가격 히스토리
- `FMP chart` — 가격 차트 데이터

## 5. Insider / Ownership

- `FMP insiderTrades` — 내부자 매매
- `FMP form13F` — 기관 보유 현황
- `PlayMCP UsStockInfo-get_holder_info` — 보조 확인

## 주의사항

- FMP와 PlayMCP UsStockInfo가 같은 수치를 다르게 보고하면 FMP를 우선하고 차이를 각주로 남긴다.
- 신규상장/소형주는 FMP 데이터가 제한적일 수 있음 — 이 경우 WebSearch로 보완하고 출처를 명시.
