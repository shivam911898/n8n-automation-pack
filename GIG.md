# Fiverr gig and Upwork copy: n8n Automation Pack

Pricing basis: `freelance_biz/research/competitors-n8n.md` (sections 4.1-4.5). The numbers below are launch prices for a seller with
zero reviews. Raise them on the schedule in "Raise to".

## Gig title (80 characters max)

**I will build n8n workflows for AI lead scoring, email triage and reports**

(72 characters. Leads with the three jobs buyers ask for, keeps "n8n", "AI" and "workflows" for search.)

Other titles to test (swap after about 2 weeks if impressions are low):

- `I will set up self-hosted n8n and AI workflows, a Zapier or Make alternative` - captures migration and Zapier-alternative searches
- `I will build n8n automations for invoices, Shopify alerts and daily KPI reports`

## Packages (launch prices)

| | **Basic - $79** | **Standard - $199** | **Premium - $449** |
|---|---|---|---|
| Name | Single Workflow | Business Starter | Full Automation + Self-Host |
| Workflows | 1 from the pack, installed in your n8n | 3 from the pack | all 5 from the pack |
| Apps connected | up to 3 | up to 6 | up to 10 |
| CRM destination | - | 1 (HubSpot, Pipedrive or Airtable/Sheets) | 1 CRM |
| Customisation | settings in the Config node | settings in the Config node | custom prompts and fields |
| Error handling | error-handling branch, test run on your data | + global Error Trigger alert workflow (Slack or email) | + execution-log review after 7 days |
| Hosting | into your n8n (Cloud or existing instance) | + Docker Compose file for self-hosting | n8n + Postgres + HTTPS + nightly backups installed on **your own VPS** |
| Documentation | workflow JSON + 1-page doc | + 15-minute walkthrough video | + 45-minute handover call + runbook (backup, update, restore) |
| Revisions | 1 | 2 | 3 |
| Delivery | 3 days | 6 days | 10-12 days |
| Post-delivery support | 3 days | 7 days | 14 days |

AI steps (score, classify, draft, summarise) use your own Groq, Gemini or OpenAI key in every tier. The five workflows, their JSON and
the validator are in the repo. The global Error Trigger alert workflow, the CRM destination and custom prompts are written for the order.

## Raise to

| | Basic | Standard | Premium | When |
|---|---|---|---|---|
| Fiverr launch | $79 | $199 | $449 | 0 reviews |
| Fiverr step 2 | $99 | $279 | $599 | after 5 reviews at 4.9+ |
| Fiverr target | $129 | $349 | $799 | after about 15 reviews (or Level 2); the first draft of $100 / $300 / $750 sits between step 2 and this |
| Upwork project catalog | $100 | $300 | $650 | list at launch; raise about 20% after 5 reviews |
| Contra | from $350 (single workflow) | | from $900 (full pack) | two "from" services, not tiers |
| Upwork hourly | $35-45/hr | | | for the first contracts, then $55+ |

## Extras

- Migrate one Zapier Zap or Make scenario to n8n: $60 (the most common buyer ask)
- Extra workflow: $60
- Extra integration: $25
- Self-host on Standard: +$80
- Monthly care plan (updates, monitoring, small changes): from $50 per month
- Fast delivery (half the days): +$40

## Description (about 800 characters)

> I build n8n workflows that run in your own n8n, with no per-task fees. The three buyers ask for most:
>
> - Lead scoring: form leads scored 1-10 by AI, hot leads ping Slack (and your CRM), every lead logged to a sheet
> - Inbox triage: Gmail sorted into sales, support, invoice and spam, with draft replies you approve. Nothing is sent without a person pressing send
> - Daily KPI report: yesterday, last 7 days and a 5-line summary in Slack and email, numbers calculated in code
>
> Also in the pack: Shopify order alerts with VIP tagging and invoice/PDF intake into Google Sheets.
>
> Included: importable workflow JSON, docs, a walkthrough video (Standard and up), error handling with safe AI fallbacks, and an Error Trigger alert so a failed run reaches you (Standard and up). AI steps use your own Groq, Gemini or OpenAI key.
>
> Code: https://github.com/shivam911898/n8n-automation-pack
>
> Message me your 3 most repetitive tasks and your tools, and I will recommend a package.

## FAQ

**1. Do I need my own n8n account or server?**
Either works. Basic runs on n8n Cloud or any instance you already have. Standard adds a Docker Compose file, and I can install it on your server for +$80. Premium includes installing n8n on your own VPS (you own the server and pay the host directly) with HTTPS and nightly backups.

**2. Which apps can you connect?**
Gmail / Outlook, Google Sheets / Airtable / Notion, Slack / Telegram / Teams, Shopify / WooCommerce / Stripe, HubSpot and most CRMs, any app with an API or webhook. If n8n has no node, I use the HTTP Request node.

**3. Will the AI email my customers on its own?**
No. Reply drafts are saved as drafts for a person to approve, and numbers in reports are calculated in code, not guessed by AI. If the AI service is down the item is still logged and flagged for manual review.

**4. Can you host and run n8n for me on your server?**
No, and that is deliberate. I install n8n on your server or in your own n8n Cloud account and hand over the credentials. I never host clients on an instance I own and I never give anyone a login to mine, because n8n's Sustainable Use License does not allow that without a paid license. You pay for my work (setup, changes, monitoring), not for access to n8n. The workflow JSON I write is MIT-licensed and yours; n8n itself is under n8n's own Sustainable Use License, not MIT.

**5. What do you need from me to start?**
A short description of the process, example data (a sample email, order or invoice), and access to the tools via a dedicated account or API key you can revoke. Never send me your main password; I will show you how to create the credentials yourself during the call.

**6. Can you migrate my Zapier/Make automations?**
Yes. One Zap or Make scenario is a $60 add-on to any package. For a bigger move, such as 12-15 workflows, message me and I will send a custom offer after looking at what you run today. The logic is rebuilt in n8n; apps without an n8n node go through the HTTP Request node.

## Tags (5)

`n8n` | `n8n workflow` | `n8n automation` | `n8n ai agent` | `self hosted n8n`

## Upwork portfolio blurb

Built a pack of five production-style n8n workflows: AI lead scoring, Gmail triage with approval-only drafts, daily KPI reports, Shopify order alerts with VIP tagging and PDF invoice intake to Google Sheets. Each has one Config node for client settings, safe AI fallbacks and an offline validator script, and runs in your own n8n (Cloud or self-hosted) with no per-task fees. I can adapt any workflow to your tools, migrate Zapier or Make automations to n8n, or install the Docker/Postgres self-host stack on your server. Source (MIT): https://github.com/shivam911898/n8n-automation-pack

## Launch checklist

- [ ] Title, category and the 5 tags above entered; the pricing table matches "Launch prices", not "Raise to"
- [ ] GitHub repo https://github.com/shivam911898/n8n-automation-pack is public and the README screenshots are in `docs/` before the link goes live
- [ ] Gallery: n8n canvas with five labelled node groups, tier table showing which workflows are in each tier, "Zapier bill vs your own n8n server" slide (n8n's pricing as a footnoted range, not a guarantee)
- [ ] Video: 30-45 s from `DEMO_SCRIPT.md` (lead arrives and Slack alert fires, draft reply appears, invoice row appears in the sheet, Shopify test alert, KPI message, Error Trigger alert on a deliberately broken run)
- [ ] Offer a free sample run on the buyer's test payload in the first reply
- [ ] Upwork catalog entry at $100 / $300 / $650, Contra services from $350 and $900, Upwork hourly at $35-45 published
- [ ] Review the "Raise to" table after the 5th and 15th review
