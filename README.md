# Automated Email-to-Dropbox CV Processing & Recruitment Dashboard

Production-ready Python project for ingesting job applications over IMAP, classifying roles, parsing candidate names/CVs, uploading files to Dropbox, and presenting all applicants in a Flask dashboard.

## Features

- IMAP ingestion with first-run backfill (`SINCE 01-Jan-2026`) and incremental hourly sync (`UNSEEN`).
- Built-in hourly sync scheduler in dashboard runtime (configurable via env vars).
- Keyword role classification:
  - **Battery Expert**: `battery`, `lithium`, `lithium-ion`, `li-ion`, `expert`
  - **Sales & Marketing**: `sales`, `marketing`
- Attachment extraction for `.pdf`, `.doc`, `.docx`.
- Multi-source candidate name extraction with confidence scoring:
  - CV content = High
  - Email body = Medium
  - Email address = Low
- CV parsing via `pdfplumber` + `PyMuPDF` fallback and `python-docx`.
- Dropbox upload to structured folders and shared-link generation.
- Persistent storage in MySQL/SQLite/PostgreSQL via SQLAlchemy.
- Duplicate prevention using unique message/attachment constraints plus pre-check.
- Logging to console + rotating file logs (`logs/logs.txt`).
- Flask/Bootstrap HR dashboard with search + filters.

## Project Structure

```
.
├── app/
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── web.py
│   ├── routes/
│   │   └── dashboard.py
│   ├── services/
│   │   ├── applicant_service.py
│   │   ├── attachment_service.py
│   │   ├── classifier.py
│   │   ├── cv_parser.py
│   │   ├── dropbox_service.py
│   │   ├── imap_service.py
│   │   ├── name_extractor.py
│   │   └── sync_service.py
│   └── utils/
│       ├── helpers.py
│       ├── logging_config.py
│       └── retry.py
├── templates/
│   ├── base.html
│   └── index.html
├── .env.example
├── requirements.txt
├── main.py
└── run_dashboard.py
```

## Environment Variables

Copy `.env.example` to `.env` and set values:

- `EMAIL_USER`
- `EMAIL_PASS`
- `IMAP_SERVER`
- `IMAP_PORT`
- `DROPBOX_APP_KEY`
- `DROPBOX_APP_SECRET`
- `DROPBOX_REFRESH_TOKEN` (recommended)
- `DROPBOX_ACCESS_TOKEN`
- `DROPBOX_BASE_PATH` (default `/CVs`)
- `DATABASE_URL` (e.g. MySQL `mysql+pymysql://user:pass@host/db`)
- `APP_SECRET_KEY`
- `LOG_LEVEL`
- `ENABLE_HOURLY_SYNC` (`true`/`false`, default `true`)
- `SYNC_INTERVAL_MINUTES` (default `60`)
- `SCHEDULER_LOCK_FILE` (default `/tmp/hr_cvs_scheduler.lock`)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set DATABASE_URL with your MySQL credentials
# mysql+pymysql://zelavclr_job:Clickbaby1!@localhost/zelavclr_ies_job_applications
```

## Run Sync (cron-safe)

```bash
python3 main.py
```

Recommended cron:

```cron
0 * * * * cd /path/to/automate-cv-dropbox && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

> By default, the dashboard runtime now includes an hourly sync scheduler.
> If you disable it (`ENABLE_HOURLY_SYNC=false`), use cron with `python3 main.py` to keep ingestion running.


## Automated Hourly Sync

When the Flask dashboard starts (`run_dashboard.py` / `passenger_wsgi.py`), it now starts a background scheduler that runs the full email -> parse -> Dropbox upload flow once every hour by default.

- Disable it with `ENABLE_HOURLY_SYNC=false`
- Change frequency with `SYNC_INTERVAL_MINUTES=<minutes>`
- Change cross-process lock file with `SCHEDULER_LOCK_FILE=<path>`
- Manual **Run Sync Now** remains available in the UI

The scheduler now waits one interval before its first automatic run and uses a process-level lock so only one web worker executes sync at a time.

For deployments where you prefer cron-only execution, disable the scheduler and keep your existing cron for `python3 main.py`.

## Run Dashboard

```bash
python3 run_dashboard.py
```

Then visit `http://localhost:5000`.

## Notes

- Dropbox auth supports:
  - **Recommended:** `DROPBOX_APP_KEY` + `DROPBOX_APP_SECRET` + `DROPBOX_REFRESH_TOKEN`
  - **Fallback:** `DROPBOX_APP_KEY` + `DROPBOX_APP_SECRET` + `DROPBOX_ACCESS_TOKEN`
  - **Legacy fallback:** `DROPBOX_ACCESS_TOKEN` only
- `.doc` extraction is accepted as attachment type, but legacy DOC text parsing is limited unless external converters are installed.
- First successful run sets `sync_state.initial_backfill_complete=true`; later runs fetch only unseen emails.


## Deploy on Namecheap (cPanel Python App)

This project already uses **Flask** (`Flask==3.1.0`) and exposes a WSGI app for hosting.

### 1) Create the Python app in Namecheap
Use cPanel → **Setup Python App** → **Create Application** with values like:

- **Python version:** 3.11 (or latest available 3.x)
- **Application root:** `hr_cvs` (or your chosen folder)
- **Application URL:** your domain/subdomain
- **Application startup file:** `passenger_wsgi.py`
- **Application Entry point:** `application`

### 2) Upload project files
Upload this repository into your selected **Application root**.

### 3) Install dependencies in the app virtualenv
From cPanel terminal (or SSH):

```bash
cd ~/hr_cvs
pip install -r requirements.txt
```

### 4) Configure environment variables
In **Environment variables** (same screen), add your required values:

- `EMAIL_USER`, `EMAIL_PASS`, `IMAP_SERVER`, `IMAP_PORT`
- `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_REFRESH_TOKEN` (recommended)
- `DATABASE_URL`
- `APP_SECRET_KEY`
- `LOG_LEVEL`
- `ENABLE_HOURLY_SYNC` (`true`/`false`, default `true`)
- `SYNC_INTERVAL_MINUTES` (default `60`)
- `SCHEDULER_LOCK_FILE` (default `/tmp/hr_cvs_scheduler.lock`)

### 5) Initialize/restart
- Click **Restart** for the Python app in cPanel after changes.
- If using MySQL on Namecheap, make sure `DATABASE_URL` points to the cPanel DB host/user/password/db.

### 6) Verify
Open your configured URL and confirm the dashboard loads.

> Note: `main.py` is your sync worker entrypoint (for cron), while `passenger_wsgi.py` is the web WSGI entrypoint.
