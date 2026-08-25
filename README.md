````markdown
# 📊 Option Trader

A web-based dashboard and automation system for managing historical market data for the Option Trader project.

---

# 🏗️ System Architecture

```text
Netlify Dashboard
        ↓
Netlify Function
        ↓
GitHub API
        ↓
GitHub Actions Workflow
        ↓
Python Script
        ↓
Angel One API
        ↓
Updated CSV Files
        ↓
Git Commit & Push
        ↓
GitHub Repository Updated
        ↓
Dashboard Refreshes Latest Dates
````

---

# 📁 Project Structure

```text
Option_trader/
│
├── connection.py
├── download_historical.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── nifty50_daily.csv
│   ├── banknifty_daily.csv
│   ├── nifty_midcap50_daily.csv
│   ├── nifty_vix.csv
│   └── backup/
│
├── .github/
│   └── workflows/
│       ├── update_historical.yml
│       └── test_connection.yml
│
├── netlify/
│   └── functions/
│       ├── update-historical.js
│       └── test-connection.js
│
├── index.html
├── style.css
├── app.js
└── netlify.toml
```

---

# 📊 Market Data

Historical daily OHLC data is maintained for:

| Instrument      | Symbol          | Token    | File                            |
| --------------- | --------------- | -------- | ------------------------------- |
| Nifty 50        | Nifty 50        | 99926000 | `data/nifty50_daily.csv`        |
| Bank Nifty      | Nifty Bank      | 99926009 | `data/banknifty_daily.csv`      |
| Nifty Midcap 50 | NIFTY MIDCAP 50 | 99926014 | `data/nifty_midcap50_daily.csv` |
| India VIX       | India VIX       | 99926017 | `data/nifty_vix.csv`            |

Each CSV contains:

```text
datetime
open
high
low
close
volume
```

---

# 🔐 Angel One Connection

The Angel One SmartAPI connection is managed by:

```text
connection.py
```

The main function is:

```python
get_connection()
```

The connection system:

* Reads credentials from environment variables.
* Generates TOTP automatically using PyOTP.
* Creates an Angel One SmartAPI session.
* Reuses the same connection during execution.
* Automatically reconnects when the session becomes older than 7.5 hours.

Required credentials:

```text
ANGEL_API_KEY
ANGEL_CLIENT_ID
ANGEL_PASSWORD
ANGEL_TOTP_KEY
```

These credentials must never be committed to GitHub.

They are stored securely as GitHub Secrets.

---

# 🔄 Historical Data Update

The main historical data script is:

```text
download_historical.py
```

The update process is:

```text
Existing CSV
      ↓
Check latest available date
      ↓
Create backup
      ↓
Fetch missing data from Angel One
      ↓
Append new data
      ↓
Remove duplicate dates
      ↓
Sort chronologically
      ↓
Save updated CSV
```

Example:

```text
Existing data:
2021-01-01 → 2026-08-20

        ↓

Create backup

        ↓

Fetch missing data:
2026-08-21 → Today

        ↓

Append new candles

        ↓

Remove duplicates

        ↓

Save updated file
```

The purpose is to fetch only the missing data instead of downloading the complete history every time.

---

# 💾 Backup System

Before updating a CSV file, the existing file is copied to:

```text
data/backup/
```

The backup filename includes the latest date from the original file.

Example:

```text
nifty50_daily_2026-08-20.csv
```

This ensures that the previous version of the historical data is preserved before any update is performed.

---

# 🖥️ Netlify Dashboard

The dashboard is hosted on Netlify:

[Option Trader Dashboard](https://optionmaster.netlify.app/?utm_source=chatgpt.com)

The dashboard acts as the control panel for the project.

Current actions include:

```text
🔄 Update Historical Data

🔌 Test Angel One Connection
```

The dashboard does not directly connect to Angel One using browser-side credentials.

Instead, it communicates with Netlify Functions.

---

# 🔄 Update Historical Data Workflow

When the user clicks:

```text
🔄 Update Historical Data
```

the complete workflow is:

```text
User clicks button
        ↓
app.js
        ↓
Netlify Function
        ↓
GitHub API
        ↓
GitHub Actions Workflow
        ↓
update_historical.yml
        ↓
download_historical.py
        ↓
connection.py
        ↓
Angel One SmartAPI
        ↓
Latest market data fetched
        ↓
CSV files updated
        ↓
Git Commit
        ↓
Git Push
        ↓
GitHub Repository Updated
        ↓
Dashboard refreshes latest data dates
```

---

# 🔌 Test Angel One Connection

The dashboard also contains:

```text
🔌 Test Angel One Connection
```

This triggers a separate GitHub Actions workflow.

The connection test performs:

```text
GitHub Secrets
        ↓
connection.py
        ↓
Angel One Login
        ↓
SmartAPI Connection
        ↓
Fetch Nifty LTP
```

A successful test confirms that:

* API key is valid.
* Client ID is valid.
* Password is valid.
* TOTP secret is valid.
* Angel One login works.
* SmartAPI connection works.

---

# ⚙️ GitHub Actions

GitHub Actions is used as the execution environment for the Python scripts.

Main workflows:

```text
.github/workflows/test_connection.yml
```

Used to test the Angel One connection.

```text
.github/workflows/update_historical.yml
```

Used to update the actual historical CSV files.

The update workflow performs:

```text
1. Checkout repository
        ↓
2. Set up Python
        ↓
3. Install dependencies
        ↓
4. Load Angel One credentials from GitHub Secrets
        ↓
5. Run download_historical.py
        ↓
6. Check for changed files
        ↓
7. Commit updated CSV files
        ↓
8. Push changes to GitHub
```

---

# 🌐 Netlify Functions

Netlify Functions act as a secure bridge between the dashboard and GitHub.

The flow is:

```text
Browser
    ↓
Netlify Function
    ↓
GitHub API
    ↓
GitHub Actions
```

The browser never receives the GitHub token directly.

The Netlify Function securely uses the token stored in Netlify environment variables to trigger GitHub Actions workflows.

---

# 🔑 Netlify Environment Variables

Netlify stores the GitHub configuration required by the functions.

Typical variables:

```text
GITHUB_OWNER
GITHUB_REPO
GITHUB_TOKEN
GITHUB_WORKFLOW
```

Example:

```text
GITHUB_OWNER=ayskhare
GITHUB_REPO=Option_trader
GITHUB_WORKFLOW=update_historical.yml
```

`GITHUB_TOKEN` must be stored as a secret environment variable.

The token requires permission to trigger GitHub Actions workflows.

---

# 🔒 GitHub Secrets

The following Angel One credentials are stored as GitHub Secrets:

```text
ANGEL_API_KEY
ANGEL_CLIENT_ID
ANGEL_PASSWORD
ANGEL_TOTP_KEY
```

These are accessed only by GitHub Actions during workflow execution.

They should never be stored in:

```text
connection.py
download_historical.py
app.js
index.html
GitHub repository
```

---

# 🛡️ Security Architecture

```text
Browser
   │
   │ No sensitive credentials
   ▼
Netlify Dashboard
   │
   ▼
Netlify Function
   │
   │ Uses GitHub Token securely
   ▼
GitHub API
   │
   ▼
GitHub Actions
   │
   │ Uses Angel One GitHub Secrets
   ▼
Python Scripts
   │
   ▼
Angel One SmartAPI
```

The following must never be exposed in frontend code:

```text
ANGEL_API_KEY
ANGEL_CLIENT_ID
ANGEL_PASSWORD
ANGEL_TOTP_KEY
GITHUB_TOKEN
```

---

# 🖥️ Dashboard Output

The dashboard includes a display area for showing the status of operations.

The intention is to show meaningful process information such as:

```text
[10:30:12] Starting historical data update...

[10:30:15] GitHub Actions workflow triggered.

[10:30:20] Updating Nifty 50...
[10:30:21] Last available date: 2026-08-20

[10:30:25] Updating Bank Nifty...

[10:30:35] Updating Nifty Midcap 50...

[10:30:45] Updating India VIX...

[10:31:00] Historical data update completed successfully.
```

The Python scripts control their own output using `print()` statements, while the dashboard can display workflow status and execution information.

---

# 🔁 Complete End-to-End Production Flow

```text
┌─────────────────────────┐
│         USER            │
└────────────┬────────────┘
             │
             │ Clicks Update Historical Data
             ▼
┌─────────────────────────┐
│   NETLIFY DASHBOARD     │
│                         │
│ index.html              │
│ app.js                  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    NETLIFY FUNCTION     │
│                         │
│ update-historical.js    │
└────────────┬────────────┘
             │
             │ GitHub API request
             ▼
┌─────────────────────────┐
│       GITHUB API        │
└────────────┬────────────┘
             │
             │ workflow_dispatch
             ▼
┌─────────────────────────┐
│     GITHUB ACTIONS      │
│                         │
│ update_historical.yml   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     PYTHON SCRIPT       │
│                         │
│ download_historical.py  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   ANGEL ONE CONNECTION  │
│                         │
│ connection.py           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    ANGEL ONE SMARTAPI   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      MARKET DATA        │
│                         │
│ Nifty 50                │
│ Bank Nifty              │
│ Nifty Midcap 50         │
│ India VIX               │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      CSV UPDATE         │
│                         │
│ Check latest date       │
│ Backup existing file    │
│ Fetch missing data      │
│ Append data             │
│ Remove duplicates       │
│ Save updated CSV        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      GIT COMMIT         │
│                         │
│ Updated CSV files       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       GIT PUSH          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   GITHUB REPOSITORY     │
│       UPDATED           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       DASHBOARD         │
│                         │
│ Shows latest data dates │
└─────────────────────────┘
```

---

# 🧪 Local Development

Clone the repository:

```bash
git clone <repository-url>
cd Option_trader
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure:

```text
ANGEL_API_KEY
ANGEL_CLIENT_ID
ANGEL_PASSWORD
ANGEL_TOTP_KEY
```

Test the Angel One connection:

```bash
python connection.py
```

Run the historical data update:

```bash
python download_historical.py
```

---

# 📦 Technology Stack

| Component           | Technology            |
| ------------------- | --------------------- |
| Frontend            | HTML, CSS, JavaScript |
| Website Hosting     | Netlify               |
| Server-side Layer   | Netlify Functions     |
| Workflow Triggering | GitHub API            |
| Automation          | GitHub Actions        |
| Backend             | Python                |
| Market Data         | Angel One SmartAPI    |
| Historical Storage  | CSV                   |
| Data Processing     | Pandas                |
| TOTP                | PyOTP                 |
| Source Control      | GitHub                |

---

# 🚀 Future Direction

The current historical data system is the foundation for the larger Option Trader project.

The planned system can grow as:

```text
Historical Market Data
        ↓
Data Analysis
        ↓
Option Strategy Analysis
        ↓
Signal Generation
        ↓
Risk Management
        ↓
Trade Execution
        ↓
Position Monitoring
        ↓
Performance Tracking
```

The current architecture separates responsibilities clearly:

```text
Netlify
    ↓
User Interface

Netlify Functions
    ↓
Secure Trigger Layer

GitHub Actions
    ↓
Python Execution Layer

Python
    ↓
Data Processing

Angel One SmartAPI
    ↓
Market Data

CSV Files
    ↓
Historical Data Storage

```
```
