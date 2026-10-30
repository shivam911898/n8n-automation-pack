# Self-host stack: n8n + PostgreSQL

A small, production-minded stack for running n8n on a client's own VPS: n8n, PostgreSQL (not the default SQLite),
persistent volumes, execution pruning, binary data kept on disk, and HTTPS through Coolify, Caddy or Traefik.

Sizing: 2 vCPU / 2 GB RAM is enough for this pack (about 5 EUR / USD per month on Hetzner, DigitalOcean, Vultr).

Files: `docker-compose.yml`, `.env.example`. Nothing else is needed.

## Deploy with Coolify (about 10 steps)

Coolify is a free, self-hosted deploy panel that handles Docker, HTTPS certificates and redeploys.

1. **Create the server.** Fresh Ubuntu 24.04 VPS (2 vCPU / 2 GB). Add your SSH key. The client should own the account and pay the bill.
2. **Install Coolify** (official one-liner from the Coolify docs, run as root): `curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash`. Open `http://SERVER_IP:8000` and create the admin user.
3. **Point DNS.** Create an `A` record `n8n.clientdomain.com` -> server IP. Wait until it resolves.
4. **New project.** In Coolify: Projects -> New -> Production -> `+ New Resource`.
5. **Add the stack.** Pick *Docker Compose Empty* and paste `docker-compose.yml` (or choose *Public/Private Repository* and point at this folder). Shortcut: Coolify also has a one-click *n8n with PostgreSQL* service; use it if you do not need the pruning and binary-data settings above.
6. **Set environment variables** (Environment Variables tab; use `.env.example` as the list). Generate `N8N_ENCRYPTION_KEY` with `openssl rand -hex 32`, set a long `POSTGRES_PASSWORD`, `N8N_HOST=n8n.clientdomain.com`, `WEBHOOK_URL=https://n8n.clientdomain.com/`, and the client's `GENERIC_TIMEZONE`.
7. **Set the domain.** On the `n8n` service enter `https://n8n.clientdomain.com:5678` (the `:5678` tells Coolify the container port). Coolify's Traefik proxy issues the Let's Encrypt certificate. Leave the commented Traefik/Caddy blocks in the compose file alone.
8. **Deploy.** Press Deploy. Postgres must turn healthy first; n8n starts after it. First boot takes about a minute.
9. **Create the owner account.** Open `https://n8n.clientdomain.com`, register the owner (the client's email), then *Workflows -> Import from file* for each JSON in `../workflows/`.
10. **Hand over.** Save `N8N_ENCRYPTION_KEY` and the DB password in the client's password manager, enable a Coolify scheduled backup (or the cron below), add credentials, edit each **Config** node, run the test payloads, activate.

No Coolify? Plain Docker works the same: install Docker, copy this folder, `cp .env.example .env`, edit it, then `docker compose up -d`. For HTTPS uncomment the Caddy block in the compose file (and create a one-line `Caddyfile`).

## Backup

Run from the folder that contains `docker-compose.yml` and `.env`:

```bash
# 1) database dump (workflows, credentials (encrypted), execution history, users)
mkdir -p backups && docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "backups/n8n-$(date +%F).sql.gz"

# 2) nightly at 03:00, keep 14 days (crontab -e)
0 3 * * * cd /opt/n8n && mkdir -p backups && docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > backups/n8n-$(date +\%F).sql.gz && find backups -name '*.sql.gz' -mtime +14 -delete
```

Copy `backups/` off the server (S3 / Backblaze / the client's Drive via `rclone`). A backup on the same disk is not a backup.

Restore into an empty stack: `gunzip -c backups/n8n-2026-10-30.sql.gz | docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'`. The restored credentials only decrypt with the **same** `N8N_ENCRYPTION_KEY`.

Workflow-only export (handy for Git): `docker compose exec -T n8n n8n export:workflow --all --separate --output=/home/node/.n8n/export/`.

## Update

```bash
# 1) back up first (above), 2) read the release notes, 3) then:
docker compose pull n8n && docker compose up -d n8n
docker compose logs -f n8n      # wait for "Editor is now accessible"
```

With a pinned version: change `N8N_VERSION` in `.env` (or in Coolify) and redeploy. Update postgres only through a planned major-version migration; leave `postgres:16-alpine` alone.

## Hardening checklist

- Firewall: allow only 22, 80, 443 (Coolify panel on 8000 only from your IP, or put it behind its own domain).
- n8n owner account with a strong password and 2FA (Settings -> Personal).
- Public webhooks: set `allowedOrigins` on the Webhook node to the client's domain; add Header Auth for machine-to-machine hooks.
- Use a **paid-tier** AI API key (Groq, Gemini or OpenAI) for client data, and check the provider's current terms on whether free-tier prompts may be retained or used to improve products.
- Enable the Coolify notification (email / Telegram) for failed deployments, plus an n8n error workflow if you sell a monitoring add-on.

## About the n8n license (plain English, not legal advice)

n8n is **source-available under the Sustainable Use License**, not an OSI open-source license. The practical reading for freelancers:

- **Fine:** building workflows for a client; installing and configuring n8n on the **client's own server or account**; running n8n for your own business; consulting, training and support priced as services.
- **Fine:** the client owns the instance (their VPS, their domain, their card) and you work in it as a consultant or maintainer.
- **Needs n8n's paid license (Embed / Enterprise):** hosting many clients on **one instance that you run** and charging for access; offering n8n (or a thin wrapper) as a hosted product or SaaS; white-labelling or hiding n8n's branding in something you sell.
- Do not remove n8n license notices or branding.

Rule of thumb: sell the **work**, not **access to n8n**. If a deal blurs that line, read the current terms at docs.n8n.io (Sustainable Use License and the licensing FAQ) or ask n8n at license@n8n.io before you sign. Features marked Enterprise also need a paid licence key even on a client's server.
