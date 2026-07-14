#!/usr/bin/env python3
"""
리멤버(rememberapp.co.kr) 개인명함첩 xlsx  ->  Notion People DB 동기화

- xlsx는 표준 라이브러리만으로 파싱(zipfile + xml.etree, openpyxl 등 외부 의존성 없음)
- "명함 등록일" 기준 체크포인트 이후(=신규)만 Notion에 새 페이지로 생성
- 체크포인트 없으면(최초 실행) People DB 전체를 스캔해 현재 최신 명함등록일을 찾아 시드
- People DB는 curated 관계 자산 DB이므로, 생성 전 전화번호로 기존 레코드와 중복 여부를 확인해 중복 생성을 피함
- dry-run 기본. --apply 줘야 실제로 Notion에 씀.

2026-07-14: 기존 동기화 대상이던 "연락처" DB가 삭제되어 People DB로 리다이렉트됨.
People DB에는 연락처 DB에 있던 부서/회사폰/팩스/명함첩/그룹 필드가 없어 Notes 필드에 묶어서 보존함.

사용법:
    python3 remember_sync.py <xlsx_path>            # 무엇이 새로 들어갈지 미리보기만
    python3 remember_sync.py <xlsx_path> --apply     # 실제 Notion에 생성 + 체크포인트 갱신
"""
import os, sys, re, json, time, datetime, zipfile
import xml.etree.ElementTree as ET
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "remember_sync_state.json")

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

PEOPLE_DB = "c4713375-ffd4-4bb1-b6aa-61e61e55d78c"  # 👥 People (data source: d723da41-7700-48f9-81cf-5a3fb4a71fd8)

# xlsx 컬럼 순서 (헤더 그대로): 회사,이름,부서,직함,전자 메일 주소,근무지 주소 번지,근무처 전화,근무처 팩스,휴대폰,명함 등록일,명함첩 이름,그룹,메모
COL = {"company": 0, "name": 1, "dept": 2, "title": 3, "email": 4, "addr": 5,
       "office_phone": 6, "fax": 7, "mobile": 8, "reg_date": 9, "book": 10, "groups": 11, "memo": 12}


def load_env():
    p = os.path.join(HERE, ".env")
    env = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


ENV = load_env()
TOKEN = ENV["NOTION_TOKEN"]


# ---------- xlsx 파싱 (stdlib only) ----------

def col_letter_to_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def parse_xlsx(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                texts = si.findall(".//m:t", NS)
                shared.append("".join(t.text or "" for t in texts))

        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in z.namelist():
            candidates = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet")]
            if not candidates:
                raise SystemExit("워크시트를 찾을 수 없음: %s" % path)
            sheet_name = sorted(candidates)[0]

        root = ET.fromstring(z.read(sheet_name))
        sheet_data = root.find("m:sheetData", NS)
        rows_out = []
        for row in sheet_data.findall("m:row", NS):
            cells = {}
            for c in row.findall("m:c", NS):
                ref = c.get("r")
                col_idx = col_letter_to_index(ref)
                t = c.get("t")
                v_el = c.find("m:v", NS)
                if t == "s" and v_el is not None:
                    val = shared[int(v_el.text)]
                elif t == "inlineStr":
                    is_el = c.find("m:is", NS)
                    val = "".join(t2.text or "" for t2 in is_el.findall(".//m:t", NS)) if is_el is not None else ""
                elif v_el is not None:
                    val = v_el.text
                else:
                    val = ""
                cells[col_idx] = val
            width = max(cells.keys(), default=-1) + 1
            rows_out.append([cells.get(i, "") for i in range(width)])
        return rows_out


KOREAN_DATE_RE = re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일")


def parse_korean_date(s):
    if not s:
        return None
    m = KOREAN_DATE_RE.search(s)
    if not m:
        return None
    y, mo, d = (int(x) for x in m.groups())
    return datetime.date(y, mo, d)


def normalize_phone(s):
    return re.sub(r"\D", "", s or "")


# ---------- Notion API (stdlib only, notion-obsidian-sync/sync.py 패턴 재사용) ----------

def notion_request(method, path, body=None, retries=5):
    req = urllib.request.Request(
        "https://api.notion.com/v1" + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        method=method,
    )
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body_txt = e.read().decode(errors="replace")
            if e.code == 429 or e.code >= 500:
                wait = min(60, 3 * (2 ** attempt))
                sys.stderr.write("  notion 재시도 %d/%d (HTTP %d) %ds 대기\n" % (attempt + 1, retries, e.code, wait))
                time.sleep(wait)
                last = e
                continue
            raise SystemExit("Notion API 오류 %d: %s" % (e.code, body_txt))
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            wait = min(60, 3 * (2 ** attempt))
            sys.stderr.write("  notion 재시도 %d/%d (%s) %ds 대기\n" % (attempt + 1, retries, e, wait))
            time.sleep(wait)
    raise SystemExit("Notion API 실패: %s" % last)


def fetch_all_people():
    rows, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        d = notion_request("POST", "/databases/%s/query" % PEOPLE_DB, body)
        rows.extend(d["results"])
        if not d.get("has_more"):
            break
        cursor = d["next_cursor"]
    return rows


def date_value(page, prop_name):
    p = page["properties"].get(prop_name)
    if not p:
        return None
    d = p.get("date")
    if not d or not d.get("start"):
        return None
    return datetime.date.fromisoformat(d["start"][:10])


def phone_value(page):
    p = page["properties"].get("Phone")
    if not p:
        return None
    return p.get("phone_number")


def compute_current_max_registered_date():
    """People DB 전체를 스캔해 현재 명함등록일 최댓값을 찾음 (최초 1회, bootstrap용)."""
    rows = fetch_all_people()
    max_date = None
    for page in rows:
        d = date_value(page, "명함등록일")
        if d and (max_date is None or d > max_date):
            max_date = d
    return max_date, len(rows)


def load_checkpoint():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
        return datetime.date.fromisoformat(state["last_registered_date"]), state
    return None, None


def save_checkpoint(max_date, extra_note=""):
    state = {
        "last_registered_date": max_date.isoformat(),
        "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "note": extra_note,
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def build_notion_properties(row):
    def rt(text):
        return {"rich_text": [{"text": {"content": text}}]} if text else {"rich_text": []}

    def phone(text):
        return {"phone_number": text or None}

    def reg_date_prop(text):
        d = parse_korean_date(text)
        return {"date": {"start": d.isoformat()} if d else None}

    groups_raw = (row[COL["groups"]] or "").strip()
    groups = [g.strip() for g in groups_raw.split(",") if g.strip()]

    # People DB에는 부서/회사폰/팩스/명함첩/그룹 전용 필드가 없어 Notes에 묶어서 보존
    notes_parts = []
    if row[COL["dept"]]:
        notes_parts.append("부서: %s" % row[COL["dept"]])
    if row[COL["office_phone"]]:
        notes_parts.append("회사폰: %s" % row[COL["office_phone"]])
    if row[COL["fax"]]:
        notes_parts.append("팩스: %s" % row[COL["fax"]])
    if row[COL["book"]]:
        notes_parts.append("명함첩: %s" % row[COL["book"]])
    if groups:
        notes_parts.append("그룹: %s" % ", ".join(groups))
    if row[COL["memo"]]:
        notes_parts.append(row[COL["memo"]])
    notes_text = " / ".join(notes_parts)

    return {
        "Name": {"title": [{"text": {"content": row[COL["name"]] or "(이름 없음)"}}]},
        "회사명": rt(row[COL["company"]]),
        "Role": rt(row[COL["title"]]),
        "Phone": phone(row[COL["mobile"]]),
        "Company email": rt(row[COL["email"]]),
        "Location": rt(row[COL["addr"]]),
        "명함등록일": reg_date_prop(row[COL["reg_date"]]),
        "Notes": rt(notes_text),
        "Category": {"multi_select": [{"name": "업무"}]},
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    xlsx_path = sys.argv[1]
    apply_mode = "--apply" in sys.argv[2:]

    checkpoint, state = load_checkpoint()
    if checkpoint is None:
        print("체크포인트 없음 — People DB 전체 스캔해서 현재 최신 명함등록일 계산 중 (최초 1회, 시간 걸림)...")
        checkpoint, total = compute_current_max_registered_date()
        if checkpoint is None:
            raise SystemExit("People DB에서 명함등록일 파싱 가능한 레코드를 찾지 못함 — 수동 확인 필요")
        print("  스캔 완료: 총 %d건, 현재 최신 명함등록일 = %s" % (total, checkpoint))
        save_checkpoint(checkpoint, extra_note="bootstrap scan (%d records)" % total)

    print("체크포인트(마지막 동기화된 명함등록일): %s" % checkpoint)

    rows = parse_xlsx(xlsx_path)
    header, data_rows = rows[0], rows[1:]
    print("xlsx 총 %d건 로드" % len(data_rows))

    new_rows = []
    for row in data_rows:
        d = parse_korean_date(row[COL["reg_date"]] if len(row) > COL["reg_date"] else "")
        if d and d > checkpoint:
            new_rows.append((d, row))

    new_rows.sort(key=lambda x: x[0])
    print("신규 대상(체크포인트 이후): %d건" % len(new_rows))

    if not new_rows:
        print("신규 없음. 종료.")
        return

    for d, row in new_rows[:20]:
        print("  [%s] %s / %s / %s" % (d, row[COL["name"]], row[COL["company"]], row[COL["title"]]))
    if len(new_rows) > 20:
        print("  ... 외 %d건" % (len(new_rows) - 20))

    if not apply_mode:
        print("\n(dry-run) 실제로 생성하려면 --apply 옵션을 추가하세요.")
        return

    print("중복 방지를 위해 People DB 기존 전화번호 스캔 중...")
    existing_page_rows = fetch_all_people()
    existing_phones = {normalize_phone(phone_value(p)) for p in existing_page_rows if phone_value(p)}
    print("  기존 People 레코드 %d건 (전화번호 보유 %d건)" % (len(existing_page_rows), len(existing_phones)))

    created = 0
    skipped = 0
    max_created_date = checkpoint
    for d, row in new_rows:
        mobile_norm = normalize_phone(row[COL["mobile"]])
        if mobile_norm and mobile_norm in existing_phones:
            skipped += 1
            print("  [skip] 기존 People에 동일 전화번호 존재: %s / %s" % (row[COL["name"]], row[COL["company"]]))
            if d > max_created_date:
                max_created_date = d
            continue

        props = build_notion_properties(row)
        body = {"parent": {"database_id": PEOPLE_DB}, "properties": props}
        notion_request("POST", "/pages", body)
        if mobile_norm:
            existing_phones.add(mobile_norm)
        created += 1
        if d > max_created_date:
            max_created_date = d
        if created % 20 == 0:
            print("  %d/%d 생성됨..." % (created, len(new_rows)))

    save_checkpoint(max_created_date, extra_note="synced from %s (%d new, %d skipped as dup)" % (os.path.basename(xlsx_path), created, skipped))
    print("완료: %d건 신규 생성, %d건 중복 스킵. 체크포인트 갱신 -> %s" % (created, skipped, max_created_date))


if __name__ == "__main__":
    main()
