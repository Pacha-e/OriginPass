# Handoff — 2026-11-02 (Claude orchestrator session)

## Where we are
- **Entregable 2 code is DONE and merged to `main`** of https://github.com/Pacha-e/KeyRing (PRs #38, #36, #40, #41, #29, #33, #34, #35; all CI green; integration gates PASS).
- **Deploy IN PROGRESS** to GCP VM `fullstack` (zone us-central1-c, IP 35.253.187.162) with `Agents-how-to-code/orchestration/scratch/deploy-fullstack-vm.sh` (copied to the VM as `~/deploy-keyring.sh`):
  - stops the Tutorial 8 stack in `~/repo` (restart with `docker compose up -d` there), adds 2 GB swap, clones KeyRing to `~/keyring`, writes an untracked `docker-compose.override.yml` with the public IP, builds backend → frontend → nuxt one by one, `docker compose up -d`.
  - Firewall: `allow-3000` and new `allow-3001` (tag `fullstack`), port 80 via `http-server`.
- **Next steps for the deploy:** check `sudo docker compose ps` in `~/keyring`; verify from outside:
  - `http://35.253.187.162/` Vue SPA (Entregable 1) talks to `http://35.253.187.162:3000/api`
  - `http://35.253.187.162:3001/blog` (SSG, HTML has article titles), `/properties` (SSR, server HTML has property names), `/tools/faq` (CSR, raw HTML lacks FAQ text)
  - then fill the GitHub/GCP links in `deliverables/deliverable-2/statement.docx` and email the professor before 2026-11-02 23:59.
- Deadline rule: no commits to `main` and no redeploy after 23:59 until graded.

## After the deploy: ecosystem restructuring (student approved the order)
Read in this order:
1. `Agents-how-to-code/knowledge/research/A02-jofiel-architecture.md` (Jofiel code reality, extension points with file:line)
2. `Agents-how-to-code/knowledge/research/A03-setup-and-nodes.md` (setup repo, Hermes, tower↔laptop, contradictions, open questions)
3. The roast + plan given to the student (summary): single memory contract hot/warm/cold (claude-mem / memory-service OR agentmemory / Obsidian) with one read API in Jofiel; context diet per CLI (Claude 91 skills + 549 plugin skills from 165 plugins, Kimi 208, ~17 MCPs each, ~27 KB global instructions); RAG/vector store for skills and Obsidian; split Jofiel product (`main`, generic) from personal overlay; wire Jofiel F0–F4 (base branch, provider tiers N0–N3, quota ledger central on tower, TaskSpec body+skills, laptop node via Hermes); general watchdog; agent path policy.
4. Student answers: Jofiel base = `main` (commercial, generic); Hermes model rotates (default sol 6.1, can use Claude via an open-source bridge); memory-service is the WARM layer of the 3-layer memory (hot claude-mem, warm memory-service, cold Obsidian) — do not remove it; worker provider decision postponed to 2026-11-20 (Kimi Allegretto ends) — explore more options and benchmark with real tasks; instagram cookies file belongs to the social-intelligence module.
5. Student asked next: full e2e exploration of the intended ecosystem (incl. memory), cleanup of all CLI global files (skills/MCPs/instructions bloat), RAG + vector DB for skills (per project, only truly global ones global) and memory (mainly cold/Obsidian).

## Other state
- claude-mem: provider openai-compatible → NVIDIA NIM `minimaxai/minimax-m3.1-flash`, fallback Ollama `qwen3:8b`; key in `~/.claude-mem/.env`; watchdog task `ClaudeMem-Watchdog` (10 min) logs incidents to Obsidian `Claude Code/Incidentes claude-mem.md`. Capture works for Claude, Codex, Kimi, Qwen; Gemini/Aider pending.
- Hermes/WSL: task `Hermes-WSL-Rescue` disabled (it restarted WSL every 5 min); WSL currently shut down; boot autostart kept.
- Obsidian vault reorg: plan V01 partial (`Agents-how-to-code/orchestration/scratch/V01-vault-reorg-plan/`), not applied.
- Orchestration tooling: `Agents-how-to-code/orchestration/` (dispatch.sh = Kimi, dispatch-codex.sh = Codex gpt-6.1-terra, run-wave.sh, cleanup-orphans.ps1, ship.sh, integration-check.sh, integration-gates.sh).
