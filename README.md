# Deploy and Host Hermes on Railway

Hermes Agent by Nous Research is a self-hosted AI assistant with memory, skills and scheduled tasks. This **Hermes Pro Stack** combines the native web dashboard and browser chat with a private SearXNG search service, local Chromium and persistent storage.

## About Hosting Hermes

This template uses the official **Hermes Agent v0.22.2** image, pinned by digest, with a small Railway lifecycle adapter. Both the dashboard and the gateway use the upstream s6 supervisor even when Railway owns PID 1. You can start, stop and restart the gateway from the dashboard. Initial setup does not require a Telegram or Discord bot.

### Get started

1. Deploy both services. Only **Hermes** gets a public domain. **SearXNG** stays on Railway's private network.
2. In the Hermes service's Variables tab, reveal `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`.
3. Open the Hermes public URL and sign in with username `admin` and the generated password.
4. Choose your model provider in the dashboard and supply its credentials. Language-model usage is billed by your chosen provider. No model API key is needed just to launch the dashboard.
5. Start a chat in the dashboard. Ask Hermes to research a question and save a cited report under `/opt/data/workspace/reports/`.
6. Optionally connect Telegram, Discord or another supported messaging platform from the dashboard. This is optional for browser chat.

### What this stack adds

| Included | Benefit |
| --- | --- |
| Private SearXNG service, already connected to Hermes's native search provider | Search without configuring a separate search API subscription |
| Native page extraction and local Chromium selected by default | Read pages and interact with JavaScript sites without a cloud-browser subscription |
| Research skill with a cited-report workflow | Save useful Markdown reports with source links in the persistent workspace |
| `hermes-railway-doctor` diagnostics command | Check the real supervisor, runtime, search connection and local browser without printing API keys |
| Upstream s6 gateway lifecycle adapted for Railway's wrapped runtime | Dashboard and gateway work together; gateway controls use the real supervisor |
| Unique generated login and stable signing secret | No shared default password; login sessions can survive a service restart |
| Persistent `/opt/data` volume | Keep conversations, memory, skills, model setup and workspace files across container replacement |

SearXNG forwards queries to upstream search engines; those engines can rate-limit or block requests. It is a private instance, not an anonymity guarantee. The template disables Hermes's external keyless-search fallback by default so failed searches do not silently move to another API. You can change web and browser settings in the dashboard. Local Chromium uses this service's CPU and memory; it is not an isolated desktop VM.

The bundled research skill is an additional workflow. The dashboard, chat, terminal, memory, cron, skills and backups are native Hermes features, not features invented by this template.

From the authenticated chat terminal, run `!hermes-railway-doctor` for a local status report. Add `--search --browser` to check a real example search, page extraction and local Chromium. These optional network checks query public documentation and open example.com; they do not use your model provider or reveal its credentials.

### Persistent data and restarts

Keep your projects and output inside **`/opt/data/workspace`**. Hermes's home is `/opt/data`, including its SQLite databases, configuration, credentials, sessions, memory and skills. The template seeds its research configuration only once and preserves your edits on subsequent starts. SearXNG has no user database and its settings are part of the versioned source.

Use one replica for this volume-backed personal agent. Enable Railway volume backups for important data; Hermes also provides its own backup/export controls in the dashboard. Redeployment may briefly interrupt connections. In-memory browser tabs and terminal processes do not survive container replacement; saved files and durable conversations do.

### Variables

| Service | Variable | Default / purpose |
| --- | --- | --- |
| Hermes | `PORT` | `8080`, dashboard HTTP port behind Railway HTTPS |
| Hermes | `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | `admin`, login username |
| Hermes | `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | `${{secret(32)}}`, a different password for each deployment |
| Hermes | `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | `${{secret(32)}}`, stable session-signing secret |
| Hermes | `HERMES_DASHBOARD_PUBLIC_URL` | `https://${{RAILWAY_PUBLIC_DOMAIN}}`, trusted public dashboard origin |
| Hermes | `SEARXNG_URL` | `http://${{SearXNG.RAILWAY_PRIVATE_DOMAIN}}:8080`, internal search endpoint |
| Hermes | `RAILWAY_RUN_UID` | `0`, permits initial volume repair; runtime processes then drop to the unprivileged Hermes user |
| Both | `RAILWAY_DEPLOYMENT_DRAINING_SECONDS` | `30`, graceful shutdown window |
| SearXNG | `PORT` | `8080`, private HTTP port |
| SearXNG | `SEARXNG_SECRET` | `${{secret(32)}}`, private instance signing secret |
| SearXNG | `RAILWAY_DOCKERFILE_PATH` | `Dockerfile.searxng`, builds the companion search service |

Provider credentials can be configured in the native dashboard or as the relevant environment variables. Do not paste model keys into the template's public description or README.

### Authentication and resource sizing

This is a **single-owner agent workspace**: its authenticated owner can run commands and manage provider credentials. The generated-password login uses Hermes's native auth gate, secure cookies and password-login rate limiting. For a team or long-lived internet-facing deployment, configure Hermes's recommended Nous OAuth or self-hosted OIDC provider; see the [official authentication documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard#authentication-gated-mode). Never disable the auth gate.

Start with enough memory for Hermes and the pages you browse; allow at least 2 GB for the agent and more for substantial browser workloads. SearXNG is a separate, continuously running service and adds Railway resource usage. Language-model inference is remote; no GPU or local model is bundled.

## Common Use Cases

- Run a private Hermes AI assistant with persistent memory from your browser.
- Research topics, read sources and save cited reports without separate search or browser API subscriptions.
- Keep coding files, notes, custom skills and scheduled workflows in one persistent workspace.
- Add messaging channels later while keeping the native dashboard for configuration and supervision.

## Dependencies for Hermes Hosting

- Two Railway services and a persistent volume for Hermes.
- A supported language-model provider for AI tasks; its credentials and charges are separate.
- Upstream search engines and websites must permit the requested access.

### Deployment Dependencies

- [Hermes Agent v0.22.2](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.2)
- [Official Hermes Docker documentation](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
- [SearXNG](https://docs.searxng.org/admin/installation-docker.html)
- [Template source](https://github.com/XavTo/Hermes-Railway)

## Why Deploy Hermes on Railway?

Railway supplies HTTPS, private service networking, persistent storage and deployment controls. This Hermes Agent Pro Stack connects those pieces to a native dashboard, private SearXNG search and local browsing so you can start a useful research assistant without wiring each integration yourself.
