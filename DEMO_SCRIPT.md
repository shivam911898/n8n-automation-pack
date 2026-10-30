# Loom demo script (60-90 seconds)

Goal: show a buyer that you import a workflow, fire a real request, see the result in Slack and Sheets, and that there are four more behind it.
Record at 1080p, browser zoom 110%, Slack and the Google Sheet already open in other tabs, `Config` already filled, credentials already connected, workflow 01 imported but **inactive**.

## Before you hit record (2 min)

- n8n: import all five files once, then **delete** workflow 01 so you can re-import it live (or keep a second copy). Keep 02-05 open in tabs, canvas zoomed to fit.
- Terminal with the curl ready (replace the host):
  ```bash
  curl -X POST "https://YOUR-N8N-HOST/webhook-test/lead-intake" -H "Content-Type: application/json" -d '{"name":"Dana Whitfield","email":"dana@brightpath-logistics.com","company":"BrightPath Logistics","website":"https://brightpath-logistics.com","budget":"$5,000-8,000","message":"We key in about 300 inbound quote requests a month by hand. We want intake and CRM entry automated, ideally live within 3 weeks.","source":"website"}'
  ```
- Slack channel and the `Leads` sheet visible side by side, sheet scrolled to the last row.

## Script

| Time | On screen | Say |
|---|---|---|
| 0:00-0:08 | n8n home, Workflows list | "Hi, I build n8n automations for small businesses. This is a pack of five ready-to-import workflows. I will show you the first one live, end to end." |
| 0:08-0:20 | Workflows -> Import from File -> choose `01-lead-intake-scoring.json`; canvas opens | "Importing is one click. Here is the whole workflow: a webhook from your website form, AI scoring, then Slack for hot leads and a Google Sheet for every lead." |
| 0:20-0:30 | Click **Config** node, point at sheetId / slackChannelId / threshold | "Everything client-specific lives in this one Config node: your sheet, your Slack channel, what counts as a hot lead. No digging through nodes." |
| 0:30-0:38 | Click the Webhook node -> **Listen for test event**; switch to terminal | "I will send a test lead, the kind that arrives from a contact form." |
| 0:38-0:48 | Paste and run the curl; show the instant `{"ok": true ...}` reply; back to n8n, nodes turning green | "The form gets its answer instantly, the scoring happens in the background. The AI is scoring it against the ideal-customer profile right now." |
| 0:48-1:00 | Slack: the hot-lead message (score, reason, next step); then the Sheet: new row | "Score 9 out of 10, with the reason and a suggested next step, in Slack within seconds. And the same lead is logged in the sheet. A weak lead would only land in the sheet, no noise." |
| 1:00-1:05 | n8n: open the **Parse AI Result** node output briefly | "If the AI is ever down, the lead is still logged and flagged for manual review, so nothing gets lost." |
| 1:05-1:25 | Fast scroll: 02 (labels in Gmail + draft), 03 (KPI message in Slack), 04 (Telegram order alert), 05 (PDF to sheet row); 4-5 seconds each, canvas only | "The pack also has inbox triage with draft replies you approve, a daily 8 a.m. KPI report, Shopify order alerts that tag big spenders as VIP, and invoice PDFs turned into spreadsheet rows. All numbers are calculated in code, the AI only writes the words, and nothing is sent to a customer without you." |
| 1:25-1:30 | Self-host README on screen or the gig page | "I can set this up on n8n Cloud or on your own server with backups. Message me with your top three manual tasks and I will tell you which of these fits." |

## Tips

- If a take runs long, drop the Parse node beat (1:00-1:05) first.
- Do not show real client data, API keys or the credentials page. Blur or avoid the browser's saved-password dropdown.
- Export the Loom link into the Upwork portfolio blurb and the Fiverr gig video slot (see GIG.md).
