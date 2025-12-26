# Book Club Pack Generator (OpenAgents Multi-Agent Network)

Turn a book into a ready-to-run Book Club product pack:

- **Organizer Pack**: recruitment copy, opening script, daily ops cadence (8am teaser), announcements, homework & reflection, closing script, (optional) conversion scripts  
- **Participant Pack**: daily content posts, discussion prompts, homework & reflection, action plan

✅ Supports `cycle_days` **user-defined** (1..21).  
✅ Publisher enforces **runtime validation**: daily arrays length == `cycle_days`, and `day` is continuous.

---

## What you submit (Hackathon)
- Repo link (GitHub/Gitee)
- ≤ 3 min demo video
- Project doc (architecture + agent roles + workflow)

---

## Repo Structure

- `network/` : OpenAgents network config (Studio served at `/studio`)
- `agents/`  : 6 agents (Publisher + workers)
- `schemas/` : PackV1 JSON schema
- `scripts/` : local/zeabur startup scripts
- `docs/`    : demo input + video script

---

## Local Quickstart (one command)

### Prereqs
- Python 3.11+
- OpenAgents CLI: `pip install openagents`

### Run
```bash
bash scripts/dev_up.sh