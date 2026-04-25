# swarm-lab — fleet exercise project

Tiny FastAPI "fortune cookie" service whose only job is to **emit signal into
every bot in the swarm-bots fleet** so you can watch the agents coordinate
end-to-end.

If you only remember one thing: each hook below exercises a different bot, and
they all feed through WorkItems + handoffs in the admin dashboard.

## What's inside

```
app/
  main.py        FastAPI app (/, /fortune, /fortune/{id}, /crash, /health)
  fortunes.py    in-memory dataset + lookups
  logger.py      Seq-compatible JSON logger (stdout + async POST)
tests/
  test_app.py    5 tests — one deliberately flaky (FlakyBot fuel)
.github/
  workflows/ci.yml
  dependabot.yml
```

## Running it locally

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -v
uvicorn app.main:app --reload
# browse http://localhost:8000/
```

## How each bot gets exercised

| Bot        | What triggers it                                              | How to force it quickly                                             |
|------------|---------------------------------------------------------------|---------------------------------------------------------------------|
| Logan      | Errors logged to Seq with `Application=swarm-lab`, level=error| `curl http://<host>:8000/crash` a few times                         |
| Coddy      | Issue labeled `ready-to-implement`                            | File issue 3 below, add the label                                   |
| Captain Q  | PR opened on this repo                                        | Any PR (Coddy's or a manual one) with CI green                      |
| Sentinel   | Workflow failure webhook                                      | Push a branch that breaks tests                                     |
| FlakyBot   | Same workflow failing N times over M days                     | Leave `test_intentionally_flaky_random_timing` running in CI         |
| DepBot     | Dependabot PR opened                                          | Wait — `dependabot.yml` schedules daily pip + weekly actions checks  |
| DocAgent   | Merged PR touching `src/**`                                   | Any merge that touches `app/`                                       |
| DemoAgent  | Merged PR on a tracked repo                                   | Same — merges trigger a visual recording                            |
| ReleaseBot | `/release <owner>/swarm-lab` in Mattermost                    | Type it in `swarm-bots-logs` to draft a bump + changelog            |

## Seed issues (file these after pushing the repo)

Copy-paste these into GitHub issues so the chains have something to chew on:

1. **Add `/fortune/count` returning the number of fortunes** — label: `ready-to-implement`
   - Expected: Coddy opens a PR that adds the route + test; Captain Q reviews; merge.
2. **Fortune IDs overflow when > 5** — label: `bug`
   - Expected: human picks it up manually; not a fleet exercise.
3. **Errors from `/crash` fill up Seq** — label: `ready-to-implement`, `logan`
   - Expected: Coddy wraps `/crash` in a try/except + returns 503.

## Verifying the run

From your laptop once the repo is up and traffic is flowing:

```bash
# WorkItems should start appearing:
curl -sS "https://bots.jrec.fr/admin/api/work-items?token=$ADMIN_TOKEN" | jq '.items[0:5]'

# Mattermost channel sees the chains:
MM_TOKEN=$MATTERMOST_BOT_TOKEN MM_TEAM=jre uv run python scripts/mm.py read swarm-bots-logs --limit 20 --resolve-users

# Admin dashboard for the visual version:
open https://bots.jrec.fr/admin
```

Healthy pattern to expect:

1. `@logan` posts a digest about `intentional.crash` (within 6h of first `/crash` hit, or sooner via `/logan run`).
2. Issue #3 opens from Logan's digest → you label it `ready-to-implement` → `@coddy` auto-takes.
3. `@coddy` drops a PR, `@captain-q` reviews, CI green, merge.
4. `@demo-agent` posts a video link in the PR comments.
5. A week later: `@flaky-bot` files a quarantine issue for `test_intentionally_flaky_random_timing`.
6. Any Dependabot PR → `@dep-bot` auto-merges patch bumps; tags major bumps for Captain Q.

## Bootstrap script

See `bootstrap.sh` in this folder — creates the GitHub repo, pushes the code, enables
Dependabot, and configures the swarm-platform webhook.
