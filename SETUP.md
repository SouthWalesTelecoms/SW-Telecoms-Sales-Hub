# SW Telecoms · Sales Hub: setup

A copy of Prospect Engine turned into a stand-alone CRM for South Wales Telecoms. Your uploaded customer list is the data source. Everything saves to the `swcomms-saved-deals` repo, in its own `sales-hub/` folder, so it never mixes with the pricebook's files.

## What's in it

| Page | What it does |
|---|---|
| 📞 **Caller** | One record at a time for the telesales person. Shows the phone number (tap to dial), contact details and the last calls. Each outcome is one click: 📵 No answer, 🔁 Tomorrow, 🔁 Next week, call back on a date, 📅 Appointment booked, 👎 Not interested, 🚫 Do not call, ✉️ Email info, 💷 Deal won. Each one logs the call, sets the next action date and moves on to the next record. You can filter the queue by area, sector and status. |
| 📇 **Customers** | Search and filter the whole list, and open any record to edit it. Upload a CSV or Excel file: columns are matched automatically and you can change the matching. Existing customers are matched on Hub ID, company number, email, phone or name, then either only blanks are filled or they're updated. Select rows to enrich them (website, email, phone, director, Companies House, sector), change their status or send them to the Caller. Download everything as Excel, edit it and upload it again. |
| 📍 **Local hit list** | After an appointment is booked, this shows customers on your list near it, plus new local firms from Companies House (by postcode area and sector). Add them and call them to fill the diary that day. |
| 📊 **Overview** | For management. Shows calls, appointments, deals won, new and ongoing monthly revenue (MRR), annual run rate, one-off values and open pipeline. It also has calls per day by person, MRR won by month, the team table, upcoming appointments, overdue call-backs, won deals and renewal dates, plus Excel downloads. |
| 🔎 **Prospecting** | The full Prospect Engine search and email tools. New finds can be added to the customer list with one button. |
| ✉️ **Email activity** | Emails sent through Zoho, as in Prospect Engine. |

Deal values: monthly recurring (£/month), one-off (£) and contract term (months). Total contract value and the renewal date are worked out for you.

## 1. Code repo

1. Create a new private repo under **SouthWalesTelecoms**, for example `sw-sales-hub`.
2. Upload everything in this folder, including the hidden `.streamlit` folder:

```
app.py
requirements.txt
.streamlit/config.toml
```

## 2. Data repo

Use the existing private repo `SouthWalesTelecoms/swcomms-saved-deals`. You don't need to create anything: the app makes the `sales-hub/` folder the first time it saves.

You need a GitHub token that can write to that repo:

1. Go to GitHub → Settings → Developer settings → **Fine-grained tokens**.
2. Limit the token to `swcomms-saved-deals`.
3. Set **Contents: Read and write**.

## 3. Deploy

Go to share.streamlit.io → **Create app** → pick the code repo, branch `main`, file `app.py`. Keep the app **private**, since it holds customer data.

## 4. Secrets (App settings → Secrets)

```
# Logins: everyone sees everything. Each name goes on the calls that person logs.
APP_PASSWORD = "a-shared-fallback-password"
[HUB_USERS]
Kev = "kevs-password"
Sarah = "sarahs-password"
```

Put the main settings **above** the `[HUB_USERS]` block. TOML puts every line under a `[section]` into that section.

```
# Data
GITHUB_TOKEN = "github_pat_xxxx"
GITHUB_REPO = "SouthWalesTelecoms/swcomms-saved-deals"
# GITHUB_PATH_PREFIX = "sales-hub/"   (the default; change it only if you want a different folder)

# Enrichment and local search
COMPANIES_HOUSE_KEY = "xxxx"
GOOGLE_PLACES_API_KEY = "xxxx"        # optional, finds phone numbers and websites

# Zoho (emails still go via Zoho). Give this app its own refresh token: see step 5.
ZOHO_CLIENT_ID = "1000.xxxx"
ZOHO_CLIENT_SECRET = "xxxx"
ZOHO_REFRESH_TOKEN = ""
ZOHO_LEAD_SOURCE = "SW Telecoms"

# Branding and sender
COMPANY_NAME = "South Wales Telecoms"
SENDER_EMAIL = "sales@southwalestelecoms.co.uk"
SENDER_WEBSITE = "www.southwalestelecoms.co.uk"
SENDER_PHONE = ""
SENDER_ADDRESS = ""
```

Each person sets their own name, title and phone for email signatures in the sidebar. Emails never default to Sam.

## 5. Connect Zoho (key helper)

1. Leave `ZOHO_REFRESH_TOKEN = ""` and open the app.
2. In the sidebar, open **Connect Zoho** and copy the scope it shows.
3. In api-console.zoho.eu → Self Client → **Generate Code**, paste the scope, choose 10 minutes and click Create.
4. Paste the code into the sidebar helper and click the button.
5. Copy the `ZOHO_REFRESH_TOKEN = "..."` line it gives you into Secrets, save, and reboot the app.

Two things to do in Zoho:

- **Lead Source:** In Zoho CRM → Setup → Modules → Leads → Lead Source, add a value called **SW Telecoms**. This keeps their leads separate in reports.
- **From address:** Make sure `sales@southwalestelecoms.co.uk` is a verified From address (Setup → Channels → Email → From addresses).

## 6. First run

1. Log in, then go to **📇 Customers → Upload a list**.
2. Drop in the CSV or Excel file. Check the column matching, then click **Import**.
3. Optional: select some rows → **Enrich** to fill in the gaps. It runs 25 at a time, so do it in batches.
4. Go to **📞 Caller** and start calling.

**Download and re-upload:** download the Excel file and keep the **Hub ID** column. When you upload it again, that column matches each row back to its record. Pick **Update with the sheet's values** to apply your edits, or **Only fill in blanks** to be safe.

Records marked **Not interested** or **Do not call** are left out of the Caller queue unless you filter for them on purpose.
