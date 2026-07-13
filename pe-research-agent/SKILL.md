---
name: pe-research-agent
description: Reference for the PE Research Agent automation project (repo aerok86-arch/pe-research-agent, local ~/pe-research) — daily PE/Buyout research into Notion, plus Notion→Obsidian Brain Vault ingest (daily briefings + meeting notes). Use when the user asks about pe-research automation, the meeting-sync / meeting notes pipeline, Notion→Obsidian ingest jobs, or is debugging launchd/Task Scheduler for this project.
---

# PE Research Agent

Automation suite that researches PE/Buyout industry news daily and ingests both that research and the user's own meeting notes into the Obsidian [[project-llm-wiki|Brain Vault]]. Runs across two machines: a MacBook (portable, not always on) and a stationary Windows desktop.

**Repo**: https://github.com/aerok86-arch/pe-research-agent (public)
**Local path**: `~/pe-research` (macOS) / `%USERPROFILE%\pe-research` (Windows)

## Components

| Job | What it does | Source | Schedule / platform |
|---|---|---|---|
| `daily-research` | Web-researches PE/Buyout industry news, writes a 10-section report to Notion | Web search (Tier 1/2/3 sources) | macOS launchd, weekdays 08:45 |
| `genesis-research` | Same, but scoped to Genesis PE (user's employer from 2026-08) | Web search | macOS launchd, weekdays 08:45 |
| `ingest-worker` | Drains a JSON queue (enqueued by the two jobs above) and ingests each report into the vault | `ingest-queue/pending/*.json` | macOS launchd, weekdays 09:30/14:00 + daily 21:00 |
| `meeting-sync` | Pulls new entries from the Notion "회의록" (meeting notes) DB, filters to PE/work-relevant only, ingests substantive ones as individual raw+summary vault pages | Notion 회의록 DB (checkpoint-based) | **Windows Task Scheduler only**, daily 22:30 + on logon |

All jobs run Claude Code headless (`claude --print --dangerously-skip-permissions --mcp-config .mcp.json`) against a Notion MCP integration named "PE research agent", writing into the same iCloud-synced Obsidian vault (`01-Sources/`, `00-Meta/index.md`, `00-Meta/log.md`).

## meeting-sync — filtering + design notes

The Notion 회의록 DB mixes real PE work meetings with the user's personal voice memos (kids' story recordings, golf lessons, personal HR/career conversations). meeting-sync filters to work-relevant content only:

- **Include**: deal sourcing/IR/DD, LP meetings, fundraising, biweekly/internal strategy, portfolio monitoring, work conferences
- **Exclude**: kids' recordings, golf lessons, personal family/HR matters, empty stubs
- **Ambiguous** (can't tell from title/content, e.g. personal side projects, coursework): never guessed into the vault — logged instead to `~/pe-research/state/meeting-sync-review-queue.md` for the user to triage by hand

State is checkpoint-based (`state/meeting-sync-state.json`, tracks `last_created_time`), capped at 30 items/run so a large backlog drains over several runs instead of timing out. Idempotency is by Notion page URL already present in vault frontmatter, not by the checkpoint alone.

### Why Windows-only (2026-07-13)

macOS launchd could not execute any of this project's scripts after the user's project folders were symlinked into `~/Library/CloudStorage/OneDrive-...` on 2026-07-01 — `/bin/bash` has no Full Disk Access grant, so launchd (unlike an interactive Terminal/Claude Code session, which already has FDA) gets `Operation not permitted` on every protected-path access. This silently broke `daily-research`/`genesis-research`/`ingest-worker` too; a queue item from 07-12 sat unprocessed for a day before this was caught (see [[feedback-macos-launchd-icloud-tcc]]).

Rather than fix FDA for `/bin/bash` (documented but not done — see repo README "자주 발생하는 문제"), `meeting-sync`'s schedule was moved to the Windows desktop, which is always on (the MacBook is portable and frequently closed/asleep). The macOS script (`scripts/meeting-sync.sh`) still exists for manual/interactive runs but is **not** registered with launchd, to avoid two machines writing to the same iCloud vault concurrently (has caused ` 2.md` duplicate-file sync conflicts before).

## Setup on a new machine

See the repo README for full instructions (Notion integration token, `.mcp.json`, Claude CLI login, vault path). Windows registration for meeting-sync specifically:

```powershell
cd $env:USERPROFILE\pe-research
git pull
schtasks /Create /XML "$env:USERPROFILE\pe-research\scheduler\windows\meeting-sync.xml" /TN "PE\MeetingSync" /F
schtasks /Query /TN "PE\MeetingSync" /FO LIST
```
