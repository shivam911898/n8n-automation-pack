# n8n Automation Pack

Five ready-to-import n8n workflows that remove the most common manual jobs in a small business, plus a production-minded
self-host stack (n8n + PostgreSQL + HTTPS) you can put on the client's own server.

AI steps use Groq's OpenAI-compatible API (default model `openai/gpt-oss-120b`) for classification, scoring, drafting and
summaries, and can be pointed at Gemini or OpenAI with your own key; all numbers are calculated in code, and nothing is ever sent
to a customer without a human pressing send.

> Looking for a Zapier or Make alternative with no per-task fees? This is what that looks like: flat hosting cost, your data on your server.

## What is in the pack

| # | Workflow | Business outcome | Time saved (estimate) |
|---|---|---|---|
| 01 | [Lead intake + AI scoring](workflows/01-lead-intake-scoring.json) | Website enquiries are scored 1-10 in seconds; hot leads ping Slack, every lead lands in a sheet; bots filtered | ~10 min per lead (research + triage), about 6-7 h/month at 40 leads |
| 02 | [Inbox triage + draft replies + daily digest](workflows/02-inbox-triage.json) | Mail is labelled sales / support / invoice / spam, support gets a draft reply waiting in Gmail, owner gets a 17:30 digest | ~1.5 min per email, 5-8 h/week at 50-100 emails/day |
| 03 | [Daily KPI report](workflows/03-daily-kpi-report.json) | 08:00 Slack + email: yesterday, last 7 days, trend, top products, 5-line AI summary | ~20 min/day of spreadsheet checking, about 8 h/month |
| 04 | [Shopify order alerts + VIP tagging](workflows/04-shopify-order-notify.json) | Owner sees each order on Telegram, orders are logged, big spenders are tagged VIP automatically | ~2-3 min per order, about 4-5 h/month at 100 orders |
| 05 | [Document intake (PDF to sheet)](workflows/05-document-intake.json) | Emailed invoices become sheet rows; uncertain ones are flagged for review instead of silently trusted | ~3-5 min per document, about 5 h/month at 80 documents |

Time estimates are planning figures, not measurements: they assume the manual minutes shown and the monthly volume in the last column.
Your volumes will differ; I re-run the numbers with the client during scoping.

Details, credentials, test payloads and setup steps for each workflow: [workflows/README.md](workflows/README.md).

## Quick start (about 15 minutes for the first workflow)

1. **Get n8n.** Either n8n Cloud (fastest, monthly fee) or self-host with [self-host/](self-host/README.md) (docker compose, Coolify guide, backup/update commands).
2. **Import.** Workflows -> Import from File -> pick `workflows/01-lead-intake-scoring.json` (CLI alternative: `n8n import:workflow --input=workflows/01-lead-intake-scoring.json`).
3. **Add credentials** the workflow needs (listed at the top of each section in the workflows README). The AI steps need a Groq API key (free to create at console.groq.com) stored as a Header Auth credential named `Groq API`: header `Authorization`, value `Bearer gsk_...`.
4. **Edit the `Config` node**: sheet ID, Slack channel ID, thresholds, business context. That is the only place client-specific values live.
5. **Test** with the sample curl / email in the workflows README, then switch the workflow to **Active**.

Before you hand a workflow to a client, validate the files: `python scripts/validate.py` (Python 3.12, standard library only).

## Screenshots

| | |
|---|---|
| ![01 Lead intake](docs/01-canvas.png) | ![02 Inbox triage](docs/02-canvas.png) |
| ![03 KPI report](docs/03-canvas.png) | ![04 Shopify alerts](docs/04-canvas.png) |
| ![05 Document intake](docs/05-canvas.png) | Slack alert and sheet result: `docs/slack-alert.png`, `docs/sheet-result.png` |

Screenshots are taken from a live n8n instance after import (canvas zoomed to fit); add them to `docs/` with the file names above.

## Repo layout

```
workflows/     5 workflow JSON files + per-workflow README (setup, credentials, test payloads)
self-host/     docker-compose.yml (n8n + Postgres, Coolify/Caddy/Traefik notes), .env.example, deploy/backup/update guide
scripts/       validate.py - offline structural + secret check for every workflow file
DEMO_SCRIPT.md 60-90 s screen-recording script
GIG.md         marketplace copy (Fiverr tiers, FAQ, tags, Upwork blurb)
```

## What I customise for you

- Your tools: swap Slack for Teams / Telegram / WhatsApp, Sheets for Airtable / Notion / HubSpot / your CRM, Gmail for Outlook / IMAP.
- Your rules: scoring criteria (your ideal customer), categories and label names, reply tone, VIP thresholds, report metrics and schedule.
- Your knowledge: the business context the drafts are allowed to use (hours, prices, policies), so replies never invent facts.
- Your data sources: Stripe, WooCommerce, Shopify, QuickBooks, a database, or a custom API for extraction.
- Guard rails: human approval steps, error-alert workflow, retries, rate limits, Slack alert when something fails.
- Hosting: n8n Cloud, or installation on **your** VPS with HTTPS, Postgres, nightly backups and a documented update path.
- Handover: written setup notes plus a screen-recorded walkthrough, so your team can maintain it.

## FAQ

**Do I need to be technical?** No for using the finished workflows (you edit one Config node and watch results). Importing and connecting credentials is a one-time 15-minute job that I do for you.

**n8n Cloud or self-hosted?** Cloud is simplest. Self-hosting costs about 5 USD/month for a small VPS, has no execution limits, and keeps data on your server. The self-host folder documents the whole setup.

**Why does the AI step use the HTTP Request node, not the LangChain nodes?** One simple credential, JSON-mode output, explicit retries and a model name you can change in one field; it keeps working across n8n 1.x versions. The LangChain nodes can be swapped in; see the workflows README.

**Can I use Gemini, OpenAI, Claude or a local model instead of Groq?** Yes. OpenAI and Gemini's OpenAI-compatible endpoint need only a new URL, credential and model name; the native Gemini REST API also needs a different body and one response-path line. Steps: [Using Gemini or OpenAI instead](workflows/README.md#using-gemini-or-openai-instead). To change only the Groq model, edit `aiModel` in the Config node.

**What does it cost to run?** Each lead, email or report is one short request to a small-to-mid size model, a fraction of a cent. Groq has a rate-limited free tier and pay-as-you-go pricing: check Groq's current pricing and limits; at typical small-business volumes the AI bill is usually a few dollars a month or less.

**Is client data safe?** Credentials are stored encrypted by n8n. Emails and form messages are sent to the AI provider's API (Groq by default) for processing: check the provider's current data-use terms and use a paid or business tier for client data if they require it. Drafts are never auto-sent.

**What if the AI is wrong or down?** The prompt asks for JSON in an exact schema (JSON mode is on) and the result is re-validated in code; on failure the item is still logged and flagged for manual review (`AI status = fallback`). Scores and drafts are suggestions for a person.

**Can you host n8n for me and charge monthly?** I install it on your server and maintain it as a service. Running many clients on one instance I own would require n8n's paid license; see the plain-English note in [self-host/README.md](self-host/README.md).

**What is in `validate.py`?** An offline check that each JSON file is well-formed, every node has the fields n8n expects, all connections point at real nodes, nothing is orphaned, expression references name existing nodes, and no secrets or leftover placeholders are present. It does not replace a test run inside n8n with real credentials.

## Status and honesty notes

- Built for n8n 1.x node schemas (Webhook v2, Set v3.4, IF v2.2, Code v2, HTTP Request v4.2, Google Sheets v4.5, Gmail v2.1, Slack v2.3, Telegram v1.2). If your n8n version shows a node as "unknown parameter", open and re-save that node.
- Verified so far: all five files import cleanly with `n8n import:workflow` on n8n 2.45.7 (current release at test time); node types, `typeVersion`s and top-level parameter names were checked against that release's node definitions; the AI Code nodes (Parse AI Result in 01 and 02, Format Report in 03) and the generated request bodies were unit-tested offline with Groq-style responses (valid, malformed JSON, missing `choices`, HTTP error item); workflow 01 was also run live on a local n8n against a mock Groq-compatible endpoint (200 reply, 422 for invalid/bot input, correct `Authorization: Bearer` header from the Header Auth credential, hot vs cold routing, retry after a 503, and the fallback row after malformed JSON, a response without `choices` and a persistent HTTP 500). In that test Slack and Google Sheets were replaced by local stand-in endpoints. Not yet run end-to-end against the real Groq API with the `Groq API` credential, or against real Google, Slack, Shopify, Telegram or Stripe accounts: do that with the client's credentials during setup.
- Everything runs against placeholders; no real credentials, IDs or keys are in this repository.

## License

Workflow JSON, scripts and docs: MIT (see [LICENSE](LICENSE)). n8n itself is under the n8n Sustainable Use License.

---

Built by Shivam Kumar Yadav · sak23571113@gmail.com · github.com/shivam911898
