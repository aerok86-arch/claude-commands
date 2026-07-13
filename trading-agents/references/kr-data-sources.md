# 한국 종목 데이터 소스 플레이북

한국 상장사(KOSPI/KOSDAQ)를 분석할 때 사용하는 도구와 사용 순서. TradingAgents 원본은 yfinance/Finnhub/Reddit 기반이라 한국 종목을 거의 커버하지 못한다 — 이 스킬은 아래 소스로 그 공백을 메운다.

## 0. 종목 확정

- `mcp__claude_ai_PlayMCP__opendart-find_company` — 회사명 → DART 고유번호(corp_code) + 종목코드(6자리) 확정. 동명이인 있으면 상장 여부/업종으로 구분.
- 종목코드 형식: 6자리 숫자 (예: 삼성전자 = 005930, 우선주는 끝자리가 5/7/9 등으로 다름 — 보통주 코드 사용을 기본으로 하되 사용자가 우선주를 지정하면 그대로 사용).

## 1. Fundamentals (재무·공시)

- `opendart-get_company_info` — 기본 정보(업종, 대표자, 상장일 등)
- `opendart-get_full_financial_statement` / `opendart-get_financial_account` — 최근 사업보고서/분기보고서 재무제표 (매출·영업이익·순이익·자산·부채)
- `opendart-get_financial_index` — 재무비율 (제공되면 PER/ROE/부채비율 등)
- `opendart-get_largest_shareholders` / `opendart-get_major_stock` — 지분 구조, 최대주주 변동
- `opendart-get_dividend_info` — 배당 이력
- `opendart-get_capital_change` — 유상증자/감자 등 자본변동
- `opendart-get_treasury_stock` — 자사주 매입·소각
- `opendart-get_executives` / `opendart-get_executive_stock` — 임원 현황 및 임원 지분 변동(내부자 매매 프록시)
- `opendart-get_employees` — 직원 수 추이(성장/구조조정 신호)

재무제표 연도/분기가 여러 개 조회되면 최신 것부터 최근 3개를 비교해 추세를 본다.

## 2. News / Disclosures (뉴스·공시 촉매)

- `opendart-search_disclosures` — 최근 공시 목록(제목만으로도 촉매 파악 가능: 유상증자, 소송, 신규계약, 최대주주변경 등)
- `NaverSearch-search_news` — 최근 뉴스 (기간 좁혀서 최신순 확인)
- `NaverSearch-datalab_search` — 종목명/티커 검색량 트렌드 → 관심도 변화의 정량적 프록시

## 3. Sentiment (심리·커뮤니티·유튜브)

- `NaverSearch-search_blog`, `NaverSearch-search_cafearticle` — 개인투자자 심리(블로그/카페 톤)
- `NaverSearch-search_webkr` — 일반 웹 문서(증권사 리포트 요약 글 등)
- 유튜브: 전용 MCP 도구가 없으므로 `WebSearch`로 `"<종목명> 목표주가 site:youtube.com"`, `"<종목명> 전망 유튜브"` 등을 검색 → 상위 결과의 제목/게시일/채널을 확보하고, 필요하면 `WebFetch`로 영상 페이지(설명란·상단 댓글)를 읽어 톤을 파악한다. 스크립트 전체를 못 가져올 수 있으니 제목·설명·댓글 톤을 정성적 신호로만 쓴다.
- 여러 소스가 같은 방향(예: 뉴스도, 블로그도, 유튜브도 부정적)을 가리킬 때만 "심리 강함"으로 판단하고, 소스 1개짜리 신호는 약하게 취급한다.

## 4. Price / Technical (시세·기술적 지표)

연결된 MCP 중 KRX 실시간 시세 전용 도구가 없으므로 `WebFetch`로 공개 페이지를 사용한다:

- `https://finance.naver.com/item/main.naver?code=<6자리코드>` — 현재가, 등락률, 시가총액, PER/PBR, 외국인 보유율, 52주 최고/최저
- `https://finance.naver.com/item/sise_day.naver?code=<6자리코드>` — 일별 시세(최근 며칠 추세 파악용)
- `https://finance.naver.com/item/frgn.naver?code=<6자리코드>` — 외국인/기관 수급 동향

RSI/MACD 같은 정량 지표는 이 페이지들에 직접 나오지 않을 수 있다 — 이 경우 최근 가격 흐름(상승/하락/횡보, 거래량 변화)으로 정성 판단하고 "정량 지표 미확인"이라고 명시한다. 정확한 수치가 꼭 필요하면 `WebSearch`로 "<종목명> RSI MACD" 검색해 증권사/포털 제공 값을 인용하고 출처를 남긴다.

## 주의사항

- opendart는 상장 초기 소형주나 최근 신규상장 종목은 사업보고서가 아직 없을 수 있음 — 이 경우 [미확인]으로 표기.
- 우선주/스팩/ETF/ETN은 이 워크플로우 대상이 아님(일반 보통주 기준 설계) — 해당되면 사용자에게 한계를 고지.
- 모든 KR 소스는 한국 시간 기준. 날짜 확인이 필요하면 `NaverSearch-get_current_korean_time` 사용.
