#!/usr/bin/env python3
"""MONITOR heartbeat: report repository workflow activity and alert on stale/failing runs."""
import json, os, datetime, urllib.request, urllib.error

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
now = datetime.datetime.now(datetime.timezone.utc)
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=20"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=20) as response:
    runs = json.load(response)["workflow_runs"]

# Exclude this heartbeat run when assessing the monitored work.
current_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
other = [r for r in runs if r["id"] != current_id]
recent = other[:10]
last = recent[0] if recent else None
age_min = None
if last:
    stamp = last.get("updated_at") or last.get("created_at")
    parsed = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    age_min = round((now - parsed).total_seconds() / 60, 1)

state = "IDLE"
alert = False
reason = "Nessun workflow di ricerca recente rilevato; heartbeat attivo."
if last:
    if last["status"] == "in_progress":
        state = "RUNNING"
        reason = f"Workflow in corso: {last['name']} (run #{last['run_number']})."
    elif last["conclusion"] == "failure":
        state = "ERROR"
        alert = True
        reason = f"Ultimo workflow terminato con errore: {last['name']} (run #{last['run_number']})."
    elif age_min is not None and age_min > 45:
        state = "STOPPED_OR_IDLE"
        alert = True
        reason = f"Nessun run di lavoro negli ultimi {age_min:.0f} minuti."
    else:
        state = "IDLE"
        reason = f"Ultimo run: {last['name']} — {last['conclusion'] or last['status']}, {age_min:.0f} minuti fa."

summary = {
  "checked_at_utc": now.isoformat(),
  "state": state,
  "alert": alert,
  "reason": reason,
  "last_work_run": {
      "id": last["id"], "name": last["name"], "run_number": last["run_number"],
      "status": last["status"], "conclusion": last["conclusion"],
      "updated_at": last["updated_at"], "url": last["html_url"]
  } if last else None,
  "recent_runs": [{
      "name": r["name"], "status": r["status"], "conclusion": r["conclusion"],
      "updated_at": r["updated_at"], "url": r["html_url"]
  } for r in recent[:5]]
}
os.makedirs("data/agent_status", exist_ok=True)
with open("data/agent_status/heartbeat.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
with open("data/agent_status/heartbeat.md", "w", encoding="utf-8") as f:
    f.write("# MONITOR — heartbeat\n\n")
    f.write(f"- Ultimo controllo UTC: {summary['checked_at_utc']}\n- Stato: **{state}**\n- {reason}\n")
    if last:
        f.write(f"- Ultimo run: [{last['name']} #{last['run_number']}]({last['html_url']})\n")
    f.write("\n> Questo controllo verifica le GitHub Actions, non garantisce un agente AI di ricerca continuo.\n")
print(json.dumps(summary, ensure_ascii=False))
if alert:
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
        f.write("alert=true\n")
else:
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
        f.write("alert=false\n")
