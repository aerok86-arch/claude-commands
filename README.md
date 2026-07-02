# Claude Code Commands

`~/.claude/commands/`에 넣으면 Claude Code에서 `/command-name`으로 호출 가능한 커스텀 스킬 모음.

## 사용법

```bash
# 설치
cp *.md ~/.claude/commands/
```

---

## 스킬 목록

### `/book-summary`
책을 피드하면 장별 분석·핵심 논증·인사이트를 포함한 심층 요약본 생성.

**지원 입력**: PDF · 텍스트파일 · URL · 직접 붙여넣기

**출력 구성**:
- 한줄 핵심 / 저자 배경 / 핵심 테제
- 장별 상세 요약 (논거·사례·데이터 포함)
- 핵심 개념 사전
- 저자 논증 구조 (전제 → 논거 → 결론)
- 인상적인 구절 인용
- 강점 / 한계 분석
- 핵심 인사이트 (독자 맥락 적용)
- 실천 적용 포인트
- 함께 읽을 책 추천

```
/book-summary ~/Downloads/thinking-fast-and-slow.pdf
/book-summary https://example.com/book-page
/book-summary  (이후 텍스트 직접 붙여넣기)
```

---

### `/ingest`
Brain Vault(Obsidian iCloud)에 source 1건을 표준 7단계 워크플로우로 ingest.

PDF · URL · Notion · 마크다운 자동 감지. raw 보존 + 요약 + wiki append + index/log 갱신.

```
/ingest ~/Downloads/paper.pdf
/ingest https://arxiv.org/abs/2501.00001
```

---

## 추가 예정

- `/paper-summary` — 논문 특화 (abstract·method·result·limitation 구조)
- `/meeting-notes` — 회의록 → 액션아이템 추출
- `/deal-memo` — PE 딜 메모 분석 요약
