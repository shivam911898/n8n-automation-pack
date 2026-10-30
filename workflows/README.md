# Workflows

Five importable n8n workflows (n8n 1.x JSON). In n8n: **Workflows -> (top right) ... -> Import from File**, or on a server
`n8n import:workflow --input=workflows/01-lead-intake-scoring.json`.

## Conventions used in all five

- **Config node.** Every workflow starts with a `Config` Set node. Sheet IDs, Slack/Telegram IDs, thresholds, the AI model name
  (`aiModel`) and business context live there, so a client edits one place. Values like `YOUR_GOOGLE_SHEET_ID` are placeholders to replace.
- **Credentials are placeholders.** Nodes reference credentials by name only (ids are empty). After import, open each node with a
  warning badge and pick your credential. Names used:

| Credential (type) | Name in the JSON | Used by |
|---|---|---|
| Header Auth: name `Authorization`, value `Bearer gsk_...` (your Groq API key, with the word `Bearer` and a space in front) | `Groq API` | 01, 02, 03 |
| Google Sheets OAuth2 | `Google Sheets account` | 01-05 |
| Slack API (bot token, scopes `chat:write`, `chat:write.public` or invite the bot) | `Slack account` | 01, 02, 03, 05 |
| Gmail OAuth2 | `Gmail account` | 02, 03, 05 |
| Telegram API (BotFather token) | `Telegram account` | 04 |
| Shopify Access Token (shop subdomain + Admin API token) | `Shopify Access Token account` | 04 |
| Header Auth: name `X-Shopify-Access-Token`, value = same token | `Shopify Admin token (Header Auth)` | 04 |
| Stripe API (optional) | `Stripe account` | 03 |
| Header Auth for your extraction API (optional) | `Extraction API key (Header Auth)` | 05 |

- **AI = Groq (OpenAI-compatible API) through the HTTP Request node, on purpose.** Each AI step calls
  `POST https://api.groq.com/openai/v1/chat/completions` with model `openai/gpt-oss-120b` (set in `Config.aiModel`),
  `temperature` 0.1, `max_tokens` 1024 (this model spends a few hundred tokens on reasoning before it answers) and
  `response_format: {"type": "json_object"}`. The system prompt spells out the exact JSON schema (field names
  and types). Why not the LangChain nodes: (1) one plain Header Auth credential instead of a LangChain-specific one,
  (2) JSON mode plus the schema in the prompt gives parseable JSON without an output-parser sub-node,
  (3) the model name and retries (3 tries, 3 s apart) are explicit, (4) the HTTP node has been stable across n8n 1.x versions while
  LangChain node parameters change more often. A Code node (`Parse AI Result`; `Format Report` in workflow 03) then reads
  `choices[0].message.content`, runs `JSON.parse`, validates the fields and falls back safely if the AI call failed or returned
  invalid JSON, so no lead or email is silently dropped.
  *Other Groq models:* `openai/gpt-oss-20b` (faster and cheaper, a little less careful), `qwen/qwen3.8-27b` (a third option).
  Groq retires models from time to time, so if the AI step starts failing with a "model not found" error, check Groq's current model
  list and change only `aiModel` in the `Config` node. Groq's free tier has rate limits; if you see HTTP 429 in the execution list, raise
  `waitBetweenTries` on the AI node or move to a paid tier.
  *To use the LangChain nodes instead:* replace the HTTP node with **Basic LLM Chain** + **Groq Chat Model** (or Google Gemini /
  OpenAI Chat Model), paste the same prompt text, add a **Structured Output Parser**, and change `aiJson($json)` in the Parse node
  to read the chain's `output`.

- **Untrusted text is fenced.** Emails and form messages are wrapped in `<lead>` / `<email>` tags and the prompt says to ignore
  instructions inside them. AI never writes numbers into reports (workflow 03 computes them in code) and never sends email on its own.
- **Alerts never block records.** Slack / Telegram / email nodes that sit beside a logging or tagging branch are set to
  "continue on error", so a chat outage or a wrong channel ID cannot stop the sheet row or the VIP tag. Because failures are then
  quiet, set **Settings -> Error Workflow** (or check the execution list) after go-live.
- **Test vs production URLs.** Webhook test: `/webhook-test/<path>` (works while you press *Listen for test event*). Production:
  `/webhook/<path>` (workflow must be active).
- Each canvas should get a screenshot at `docs/<nn>-canvas.png` (placeholders below; take them in n8n with the canvas zoomed to fit).

---

## Using Gemini or OpenAI instead

The pack ships with one AI node per workflow (01 `AI Score Lead`, 02 `AI Classify and Draft`, 03 `AI Write Summary`), all pointed at
Groq. To switch provider you edit that node and `Config.aiModel`; nothing else in the workflow knows which provider is used,
apart from the one response-path line in the Parse node described under B.

**A. OpenAI, or Gemini through its OpenAI-compatible endpoint.** The body shape is identical to Groq's, so only the URL, the
credential value and the model name change:

| Provider | URL | Credential value (Header Auth `Authorization`) | `Config.aiModel` example |
|---|---|---|---|
| OpenAI | `https://api.openai.com/v1/chat/completions` | `Bearer sk-...` | `gpt-4o-mini` |
| Gemini (OpenAI-compatible) | `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` | `Bearer <your Gemini API key>` | `gemini-3.1-flash-lite` |

Edit the credential (or create a new Header Auth credential and pick it in the node), change the **URL** field of the AI node, set
`aiModel`. Check that the model supports JSON mode (`response_format: json_object`). Some newer OpenAI models want
`max_completion_tokens` instead of `max_tokens`; if the API complains, rename that one field in the body. The pack has only been run
against a mock OpenAI-style endpoint and Groq-shaped responses, not against these two providers, so test one execution with the new key.

**B. Native Gemini REST (`generateContent`).** Two edits:
1. In the AI node set the URL to `https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent`, use a Header
   Auth credential named `x-goog-api-key` (value = the key, no `Bearer`), and replace the JSON body expression with the Gemini shape:

   ```js
   JSON.stringify({
     systemInstruction: { parts: [ { text: SYSTEM_PROMPT } ] },        // same prompt text as the Groq system message
     contents: [ { role: 'user', parts: [ { text: USER_TEXT } ] } ],   // same text as the Groq user message
     generationConfig: { temperature: 0.1, responseMimeType: 'application/json' }
   })
   ```
2. In the Parse node (`Format Report` in workflow 03), make `aiText` read Gemini's response shape instead of `choices[0].message.content`:

   ```js
   const aiText = (j) => {
     try { return j.candidates[0].content.parts.map((p) => p.text || '').join(''); } catch (e) { return ''; }
   };
   ```

Keep `retryOnFail`, `maxTries` and `onError: continueRegularOutput` on the node so the fallback behaviour does not change.

---

## 01 - Lead intake and AI scoring (`01-lead-intake-scoring.json`)

**What it does.** A website form POSTs a lead. The workflow replies `200` immediately, normalises the fields (and rejects bots via a
hidden `_hp` honeypot or a missing email/message with `422`), asks the AI (Groq) for a 1-10 score + one-sentence reason + next step, then:
score >= threshold (default 7) -> Slack alert **and** Google Sheets row; otherwise Sheets row only. If the AI call fails or returns
invalid JSON the lead is still logged and flagged `AI status = fallback` for manual review.

**Trigger.** Webhook `POST /webhook/lead-intake`.
**Credentials.** Groq API (Header Auth), Google Sheets, Slack.

**Setup**
1. Create the credentials above: for Groq, a Header Auth credential named `Groq API` with header `Authorization` = `Bearer gsk_...` (your key from console.groq.com). In Google Cloud enable the Sheets API for the OAuth client (n8n Cloud does this for you).
2. Create a sheet with a tab `Leads` and this header row: `Date, Name, Email, Company, Website, Budget, Message, Score, Reason, Next step, Hot, Source, AI status`.
3. Open **Config**: set `sheetId` (the long string in the sheet URL), `sheetName`, `slackChannelId` (channel details -> bottom, starts with `C`), optionally `hotScoreThreshold` and `icpDescription` (who is a good customer).
4. Invite the Slack bot to that channel (`/invite @YourBot`).
5. In the Webhook node set `allowedOrigins` to your website (default `*` is for testing).
6. Click *Listen for test event*, run the curl below, check Slack + the sheet, then toggle the workflow **Active** and switch your form to the production URL.

**Test payload** (hot lead; use `/webhook-test/` while listening):

```bash
curl -X POST "https://YOUR-N8N-HOST/webhook-test/lead-intake" \
  -H "Content-Type: application/json" \
  -d '{"name":"Dana Whitfield","email":"dana@brightpath-logistics.com","company":"BrightPath Logistics","website":"https://brightpath-logistics.com","budget":"$5,000-8,000","message":"We key in about 300 inbound quote requests a month by hand. We want intake and CRM entry automated, ideally live within 3 weeks.","source":"website"}'
```

Cold lead (should only be logged): `-d '{"name":"Sam","email":"sam@gmail.com","message":"Student project, do you offer free internships?"}'`.
Invalid (expect `422`): `-d '{"name":"x","message":"hi"}'`.
PowerShell: `Invoke-RestMethod -Method Post -Uri $url -ContentType 'application/json' -Body $json`.

Expected response: `{"ok": true, "message": "Thanks, we received your enquiry and will reply shortly."}`

![Workflow 01 canvas](../docs/01-canvas.png)

---

## 02 - Inbox triage with AI drafts and daily digest (`02-inbox-triage.json`)

**What it does.** Polls Gmail every minute for unread INBOX mail. The AI (Groq) classifies each email as `sales`, `support`, `invoice` or
`spam`, sets a priority, a one-line summary and a `needs_human` flag. The workflow applies the matching Gmail label, logs a row to a
`Triage Log` sheet and, for categories listed in `draftCategories` (default `support`), saves an AI reply as a **Gmail draft in the
same thread**. Nothing is sent automatically. A second trigger at 17:30 builds a Slack digest (counts per category and the list of
emails that need a human) from the log. Unknown or failed classifications go to `support` with `needs_human = yes`, never to spam.

**Triggers.** Gmail Trigger (every minute) and Schedule Trigger (daily 17:30) in one file; a `Manual Trigger` helper lists label IDs.
**Credentials.** Gmail, Google Sheets, Slack, Groq API (Header Auth).

**Setup**
1. In Gmail create four labels, for example `AI/Sales`, `AI/Support`, `AI/Invoice`, `AI/Spam`.
2. Run the bottom **Manual Trigger (label helper)** once (*Execute workflow* on that branch); copy each label's `id` (looks like `Label_1234567890`) into `Config.labelSales/labelSupport/labelInvoice/labelSpam`.
3. Create a sheet tab `Triage Log` with header row: `Date, From, Subject, Category, Priority, Needs human, Summary, Draft`.
4. Fill `Config`: `sheetId`, `slackChannelId`, `businessName`, and `businessContext` (hours, prices, policies; **drafts may only use facts written here**). Use `draftCategories = support,sales` to also draft sales replies.
5. Send yourself three test emails (a question, a quote request, a fake invoice). Wait up to a minute (or click *Execute workflow* with the Gmail Trigger).
6. Check labels, the drafts folder, and the sheet. Run the schedule branch manually to preview the digest. Activate.

**Test email** (support): subject `Can I move my Thursday appointment?`, body `Hi, I booked 3pm Thursday but have a meeting. Can we do Friday morning instead? Thanks, Priya`.
Expected: label `AI/Support`, a draft reply in the same thread, a new row in `Triage Log`.

![Workflow 02 canvas](../docs/02-canvas.png)

---

## 03 - Daily KPI report (`03-daily-kpi-report.json`)

**What it does.** At 08:00 reads the `Sales Log` sheet (and, if you enable it, the last 100 Stripe charges), computes **today so far,
yesterday, last 7 days and the previous 7 days** in a Code node (orders, revenue, change %, average order value, top products),
asks the AI (Groq) to turn those exact numbers into a 5-line summary (returned as JSON `{"lines": [...]}`), and sends it to Slack and
email (HTML). If the AI call fails or returns invalid JSON the report still goes out with a deterministic summary.

**Trigger.** Schedule, daily 08:00 (instance timezone, see `GENERIC_TIMEZONE`).
**Credentials.** Google Sheets, Slack, Gmail, Groq API (Header Auth); optional Stripe.

**Setup**
1. Sheet tab `Sales Log` with one row per sale: `Date` (2026-10-29 or 10/29/2026), `Amount` (numbers; `$` and commas are fine), `Product`. Different headers? Change `dateColumn/amountColumn/productColumn` in **Config**.
2. Fill `Config`: `businessName`, `currency`, `sheetId`, `salesSheetName`, `slackChannelId`, `reportEmail`.
3. Stripe is **disabled by default**. Enable the node only if Stripe is your source of truth and those sales are **not** also in the sheet (otherwise revenue is double counted). It reads up to 100 recent charges (add pagination for busier shops).
4. Click *Execute workflow* to test. Activate.

**Sample rows** to paste into the sheet for a demo (adjust dates to the last two weeks):

```
Date,Amount,Product
2026-10-29,120.50,Starter plan
2026-10-29,80.00,Add-on pack
2026-10-28,50.00,Starter plan
2026-10-25,1000.00,Annual plan
2026-10-18,40.00,Add-on pack
```

![Workflow 03 canvas](../docs/03-canvas.png)

---

## 04 - Shopify order alerts and VIP tagging (`04-shopify-order-notify.json`)

**What it does.** On every new Shopify order: formats it (customer, items, total, country, discount codes), sends a Telegram message to
the owner, appends a row to Google Sheets, and if the total is above `vipThreshold` (default 200, in shop currency) adds the tag
`VIP` to the order through the Shopify Admin API while **keeping existing tags**.

**Trigger.** Shopify Trigger, topic `orders/create` (n8n registers the webhook in Shopify when you activate).
**Credentials.** Shopify Access Token, Shopify Admin token (Header Auth), Telegram, Google Sheets.

**Setup**
1. Shopify admin -> Settings -> Apps and sales channels -> Develop apps -> create an app, Admin API scopes `read_orders`, `write_orders`, install it, copy the Admin API access token.
2. Create credentials: *Shopify Access Token* (subdomain + token) and a *Header Auth* credential named `Shopify Admin token (Header Auth)` with header `X-Shopify-Access-Token` and the same token.
3. Telegram: talk to @BotFather -> `/newbot` -> token. Send any message to the bot, open `https://api.telegram.org/bot<TOKEN>/getUpdates`, copy `chat.id`.
4. Sheet tab `Orders` header row: `Order, Date, Customer, Email, Items, Total, Currency, Country, Discount codes, VIP, Order ID`.
5. Fill `Config`: `shopDomain` (`yourstore.myshopify.com`), `telegramChatId`, `sheetId`, `vipThreshold`; bump `apiVersion` to a currently supported Shopify API version if needed.
6. Activate, then place a test order (Shopify Bogus Gateway or a draft order marked paid). Within seconds: Telegram message, sheet row, and a `VIP` tag if above the threshold.

**Testing without a store order.** Use *Listen for test event* on the trigger and place a test order, or pin a sample order (any Shopify order JSON) on the trigger node. Shopify signs its webhooks, so a plain `curl` to the trigger URL is rejected by design.

![Workflow 04 canvas](../docs/04-canvas.png)

---

## 05 - Document intake, PDF to sheet (`05-document-intake.json`)

**What it does.** Watches Gmail for unread mail with a PDF attachment (`has:attachment filename:pdf`), splits the mail into one item per
PDF (images and signatures are ignored), POSTs each PDF as `multipart/form-data` (field `file`) to **your extraction API**, writes one row per
document to Google Sheets, and posts a Slack alert whenever the document needs a human look. The workflow double-checks the API's
answer: missing vendor, number or total, or an API error, also counts as `needs_review`.

**Trigger.** Gmail Trigger (every minute, with attachment download).
**Credentials.** Gmail, Google Sheets, Slack, optional Header Auth for the API.

**Expected API response** (`200`, JSON):

```json
{
  "vendor": "Northwind Supplies Ltd",
  "number": "INV-1042",
  "date": "2026-10-28",
  "total": 1234.50,
  "currency": "USD",
  "needs_review": false
}
```

`needs_review` should be `true` when totals do not add up or confidence is low. Any service that returns this shape works: a
vision-LLM extractor with arithmetic validation (see the separate invoice-extractor demo), Google Document AI, AWS Textract or a
self-hosted OCR service behind a small wrapper.

**Setup**
1. Deploy or choose the extraction endpoint and set `Config.extractApiUrl` to its full URL (replace the `EXTRACT_API_URL` placeholder). If it needs a key, create the Header Auth credential; otherwise remove the credential from the HTTP node.
2. Sheet tab `Invoices` header row: `Received, Vendor, Invoice number, Invoice date, Total, Currency, Needs review, From, Subject, File, Gmail link`.
3. Fill `Config`: `sheetId`, `sheetName`, `slackChannelId`. Narrow the Gmail filter if needed (for example `to:invoices@yourco.com`).
4. Check the API alone: `curl -F "file=@invoice.pdf" https://YOUR-EXTRACT-API/extract`.
5. Email yourself a PDF invoice, click *Execute workflow*, verify the row; send a blank PDF to see the Slack review alert. Activate.

![Workflow 05 canvas](../docs/05-canvas.png)

---

## Validate before you ship

```bash
python scripts/validate.py
```

Checks JSON structure, node fields, connections, reachability, node-name references inside expressions, placeholder leftovers and
secret-looking strings. See the top-level README for what it does and does not prove.
