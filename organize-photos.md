---
description: NAS 사진 백업 폴더를 Memories 스타일(YYYYMMDD 장소명)로 자동 정리. exiftool+GPS 역지오코딩으로 폴더명 생성, 이벤트 클러스터링 후 이동.
argument-hint: [--execute] [--skip-geo] [--clear-cache]
allowed-tools: Bash, Write, Read
---

# /organize-photos — NAS 사진 Memories 폴더 정리

## 전제 조건

```bash
brew install exiftool   # EXIF/GPS 추출
```

## 경로 설정 (스크립트 상단 수정)

```python
BACKUP_DIR   = Path("/Volumes/homes/aerok86/Photos/MobileBackup/iPhone")
MEMORIES_DIR = Path("/Volumes/homes/aerok86/Photos/PhotoLibrary/Memories")
```

## 스크립트 위치

```
~/pe-knowledge/scripts/organize_memories.py   # 또는 /tmp/에 임시 저장
```

## 실행 순서

```bash
# 1. dry-run (계획 확인, 실제 이동 없음)
python3 organize_memories.py

# 2. 계획 검토
cat /tmp/organize_dryrun.log
cat /tmp/organize_plan.json | python3 -m json.tool | head -100

# 3. 실제 이동
python3 organize_memories.py --execute

# 캐시 초기화 후 재실행
python3 organize_memories.py --clear-cache

# GPS 역지오코딩 생략 (날짜만으로 폴더명)
python3 organize_memories.py --skip-geo
```

## 알고리즘 요약

### 이벤트 클러스터링
- 연속 촬영 간격 ≤ 36시간 AND 거리 ≤ 80km → 같은 이벤트
- 이 기준을 벗어나면 → 새 이벤트 시작

### 폴더명 규칙
| 조건 | 폴더명 형식 |
|---|---|
| 5장 이상 + 1일 | `YYYYMMDD 장소명` |
| 5장 이상 + 다일 | `YYYYMMDD~DD 장소명` |
| 5장 미만 | `YYYYMM 모음/` 에 통합 |
| GPS 없음 | `YYYYMMDD` (날짜만) |

### 역지오코딩
- Nominatim API (무료, API 키 불필요)
- Rate limit: 1 req/s (자동 준수)
- 캐시: `/tmp/geocode_cache.json` (재실행 시 재사용)
- 우선순위: city_district > suburb > county > city > town

### 임계값 수정
```python
MIN_PHOTOS_EVENT = 5    # 이하면 월별 모음
MAX_GAP_HOURS    = 36   # 이벤트 연속 최대 간격
MAX_DIST_KM      = 80   # 이벤트 최대 반경
```

## 중복 제거 선행 작업

Memories 정리 전 중복 파일 제거 권장:
→ `/private/tmp/.../scratchpad/find_duplicates_v2.py` 참고
→ `_duplicate_delete_log.txt` 로그 → `delete_from_log.py` 로 삭제

## NAS 연결

```bash
# NAS 마운트 확인
ls /Volumes/homes/

# 연결 끊긴 경우 Finder에서 smb://100.79.149.112 연결
# 또는
open "smb://100.79.149.112/homes"
```

## 파일 구조

```
/tmp/
  mobilebackup_meta.csv   # exiftool 배치 추출 결과 (캐시)
  geocode_cache.json      # GPS → 지명 캐시
  organize_plan.json      # dry-run 폴더 계획
  organize_dryrun.log     # dry-run 전체 로그
```

## 주의사항

- `--execute` 실행 전 반드시 dry-run으로 폴더 계획 검토
- 이동 후 원본(MobileBackup) 빈 폴더 자동 정리됨
- 이름 충돌 시 `파일명_1.ext` 형식으로 자동 처리
- exiftool 배치 추출: NAS 12K 파일 기준 약 10~20분 소요
- Nominatim 역지오코딩: 클러스터 수 × 1.1초 소요
