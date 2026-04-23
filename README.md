# 📄 Project Overview: Automated CV Collection & Classification System

## 🧩 Project Title
Automated Email-to-Dropbox CV Processing System

---

## 🎯 Objective
Develop a Python-based application that automatically retrieves job application emails from the company inbox (`job@interethiopia.com`), filters relevant candidates based on predefined job roles, extracts CV attachments, and uploads them to structured folders in Dropbox. The system will run on a scheduled basis and operate reliably within a shared hosting environment.

---

## 🏢 Business Context
The organization receives a high volume of job applications via email for multiple open positions, including:

- Lithium-ion Battery Expert
- Sales & Marketing

Manual sorting and storage of CVs is inefficient and error-prone. This system aims to streamline recruitment intake by automating classification and storage.

---

## ⚙️ Core Features

### 📥 Email Synchronization
- Connect to the email server using IMAP protocol
- Authenticate securely using email credentials
- Fetch unread or newly received emails from the inbox
- Run automatically every hour using a scheduled task

---

### 🔍 Email Filtering & Classification
- Analyze email subject and body content
- Detect relevant job applications using keyword matching

**Battery Role Keywords:**
- battery
- lithium
- lithium-ion
- li-ion

**Sales & Marketing Keywords:**
- sales
- marketing

- Only process emails containing relevant keywords
- Ignore unrelated emails

---

### 📎 Attachment Extraction
- Parse email content to identify attachments
- Extract CV files from email attachments
- Supported file formats:
  - PDF (.pdf)
  - Word Documents (.doc, .docx)
- Skip unsupported or irrelevant file types

---

### ☁️ Dropbox Integration
- Upload extracted CVs directly to Dropbox
- Automatically organize files into structured folders:

/CVs/Battery_Expert/YYYY-MM-DD/ /CVs/Sales_Marketing/YYYY-MM-DD/

- Ensure unique storage or overwrite handling for duplicate files
- Maintain clean and accessible cloud storage

---

### 🔁 Duplicate Processing Prevention
- Track processed emails using unique identifiers (UIDs)
- Store processed email IDs locally (e.g., text file or database)
- Prevent reprocessing of the same email

---

### ⏱️ Scheduled Execution
- Execute the application automatically every hour
- Use cron jobs in hosting environment for scheduling
- Avoid continuous background processes (shared hosting compatible)

---

### 📝 Logging & Monitoring
- Log key system activities:
  - Emails processed
  - Files uploaded
  - Errors encountered
- Maintain logs for debugging and audit purposes

---

## 🏗️ System Architecture

Email Server (IMAP) ↓ Email Fetching Module ↓ Keyword Filtering Engine ↓ Attachment Extraction Module ↓ Dropbox Upload Service ↓ Storage & Logging System

---

## 🧪 Technology Stack

| Component              | Technology               |
|----------------------|------------------------|
| Backend Language      | Python 3               |
| Email Access          | IMAP (imaplib, email)  |
| Cloud Storage         | Dropbox API            |
| Scheduling            | Cron Jobs              |
| Environment Config    | python-dotenv          |
| Hosting               | Namecheap Shared Hosting (Stellar Plus) |

---

## 🚀 Deployment Environment

- Hosted on Namecheap Stellar Plus shared hosting
- Python environment configured via cPanel
- Application executed via cron job every hour
- Secure storage of environment variables using `.env`

---

## 🔐 Security Considerations

- Use application-specific email passwords
- Protect Dropbox API access token
- Restrict file access permissions
- Avoid storing sensitive credentials in public directories

---

## 📈 Scalability & Future Enhancements

- AI-based CV parsing and candidate ranking
- Web dashboard for HR to view and manage applicants
- Automated email responses to candidates
- Integration with HR management systems
- Advanced keyword classification using NLP

---

## ✅ Expected Outcome

- Fully automated CV collection pipeline
- Organized and searchable candidate database in Dropbox
- Reduced manual workload for HR team
- Faster and more efficient recruitment process

---
