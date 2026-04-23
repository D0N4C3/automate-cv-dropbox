# Automated Email-to-Dropbox CV Processing & Recruitment Dashboard

Production-ready Python project for ingesting job applications over IMAP, classifying roles, parsing candidate names/CVs, uploading files to Dropbox, and presenting all applicants in a Flask dashboard.

## Features

- IMAP ingestion with first-run backfill (`SINCE 01-Jan-2026`) and incremental hourly sync (`UNSEEN`).
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
- Logging to console + rotating file logs.
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
- `DROPBOX_ACCESS_TOKEN`
- `DROPBOX_BASE_PATH` (default `/CVs`)
- `DATABASE_URL` (e.g. MySQL `mysql+pymysql://user:pass@host/db`)
- `APP_SECRET_KEY`
- `LOG_LEVEL`

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

## Run Dashboard

```bash
python3 run_dashboard.py
```

Then visit `http://localhost:5000`.

## Notes

- `.doc` extraction is accepted as attachment type, but legacy DOC text parsing is limited unless external converters are installed.
- First successful run sets `sync_state.initial_backfill_complete=true`; later runs fetch only unseen emails.
