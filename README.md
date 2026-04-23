# 📄 Project Overview: Automated CV Collection, Parsing & HR Dashboard System

## 🧩 Project Title
Automated Email-to-Dropbox CV Processing & Recruitment Dashboard

---

## 🎯 Objective
Develop a Python-based system that automatically retrieves job application emails from `job@interethiopia.com`, intelligently classifies applicants based on job roles, extracts CVs, identifies candidate names, uploads files to Dropbox, and provides an internal web dashboard for HR to manage and review all applicants.

---

## 🏢 Business Context
The organization receives a large number of job applications via email for roles such as:

- Lithium-ion Battery Expert  
- Sales & Marketing  

Manual handling creates inefficiencies in sorting, tracking, and reviewing candidates. This system automates the intake pipeline and provides a centralized dashboard for HR operations.

---

## ⚙️ Core Features

### 📥 Email Synchronization
- Connect to email server using IMAP
- Fetch unread/new emails from inbox
- Execute every hour via cron job
- Secure authentication using environment variables

---

### 🔍 Email Filtering & Role Classification
- Analyze subject and body of emails
- Match against predefined keyword groups

**Battery Role Keywords:**
- battery
- lithium
- lithium-ion
- li-ion
- expert

**Sales & Marketing Keywords:**
- sales
- marketing  

**REMARKS**
- Assign each application to a role category
- Ignore irrelevant emails

---

### 📎 Attachment Extraction
- Extract CV attachments from emails (and cover letters if applicable)
- Supported formats:
  - `.pdf`
  - `.doc`
  - `.docx`
- Validate file types before processing

---

## 🧠 Candidate Name Extraction Algorithm

To reliably identify the applicant’s full name, the system will implement a **multi-source extraction strategy with fallback logic**:

### 🔹 Step 1: Email Body Parsing
- Scan email body for common patterns:
  - “My name is …”
  - “I am …”
  - Signature blocks
- Use regex and NLP heuristics to extract probable names

---

### 🔹 Step 2: Email Address Parsing
- Extract name from email format:
  - `john.doe@gmail.com` → John Doe
  - `johndoe123@...` → John Doe (clean numeric suffix)
- Apply formatting:
  - Split by `.`, `_`, `-`
  - Capitalize words

---

### 🔹 Step 3: CV Content Parsing
- Extract text from CV files:
  - PDFs → `pdfplumber` / `PyMuPDF`
  - DOCX → `python-docx`
- Identify name candidates:
  - Usually top of document
  - Largest font / first line
- Apply heuristics:
  - 2–4 words
  - No numbers
  - Proper capitalization

---

### 🔹 Step 4: Confidence Scoring System
Assign scores to each source:

| Source        | Confidence |
|--------------|-----------|
| CV Content    | High      |
| Email Body    | Medium    |
| Email Address | Low       |

- Select highest-confidence result
- Fallback if higher-confidence data unavailable

---

### 🔹 Step 5: Final Normalization
- Remove special characters
- Ensure proper capitalization
- Store as: `FirstName LastName`

---

## ☁️ Dropbox Integration

- Upload CVs to structured folders:

/CVs/Battery_Expert/YYYY-MM-DD/ /CVs/Sales_Marketing/YYYY-MM-DD/

- Generate **shared Dropbox links** for each uploaded CV
- Store links for dashboard access

---

## 🗂️ Data Storage Layer

A lightweight database (SQLite or PostgreSQL) will store applicant metadata:

### 📊 Applicant Table Schema

| Field              | Description                          |
|-------------------|--------------------------------------|
| id                | Unique identifier                    |
| full_name         | Extracted candidate name             |
| email             | Applicant email address              |
| role              | Detected job category                |
| cv_file_name      | Original file name                   |
| dropbox_link      | Shareable Dropbox URL                |
| date_applied      | Timestamp                            |
| processed         | Boolean flag                         |

---

## 🌐 Web Dashboard for HR

### 🧑‍💼 Purpose
Provide HR with a clean interface to:
- View all applicants
- Access CVs instantly
- Filter and search candidates

---

### 🖥️ Dashboard Features

#### 📋 Applicant List View
- Table displaying:
  - Full Name
  - Email
  - Role
  - Date Applied
  - CV Link (clickable)

---

#### 🔎 Search & Filtering
- Filter by:
  - Role (Battery / Sales)
  - Date range
- Search by:
  - Name
  - Email

---

#### 🔗 CV Access
- Direct link to Dropbox file
- Opens in new tab

---

#### 📊 Status Tracking (Optional Enhancement)
- Add statuses:
  - New
  - Reviewed
  - Shortlisted
  - Rejected

---

### 🧰 Tech Stack (Dashboard)

| Layer        | Technology         |
|-------------|------------------|
| Backend     | Flask (Python)   |
| Frontend    | HTML, CSS, JS    |
| UI Framework| Bootstrap        |
| Database    | SQLite / PostgreSQL |

---

## 🏗️ System Architecture

Email Server (IMAP) ↓ Email Fetcher (Cron आधारित) ↓ Filtering & Classification Engine ↓ Attachment Extractor ↓ Name Extraction Algorithm ↓ Dropbox Upload + Link Generation ↓ Database Storage ↓ Flask Web Dashboard (HR Access)

---

## ⏱️ Scheduling & Execution

- Cron Job runs every hour:

0 * * * * python3 /home/user/app/main.py

- Ensures:
  - No continuous processes
  - Hosting compatibility

---

## 📝 Logging & Monitoring

- Track:
  - Processed emails
  - Extracted names
  - Upload success/failure
- Store logs in file or database

---

## 🔐 Security Considerations

- Use environment variables for credentials
- Secure Dropbox API token
- Restrict dashboard access (basic auth or login system)
- Prevent unauthorized file access

---

## 🚀 Deployment Plan

- Host backend and dashboard on Namecheap Stellar Plus
- Configure Python app via cPanel
- Set cron jobs for automation
- Deploy Flask app for internal HR access

---

## 📈 Future Enhancements

- AI-powered CV parsing (skills, experience extraction)
- Candidate ranking system
- Email auto-response system
- Multi-role classification using NLP
- Admin analytics dashboard
- Integration with HR tools (ATS systems)

---

## ✅ Expected Outcome

- Fully automated recruitment intake system
- Accurate candidate identification (name extraction)
- Organized cloud storage with direct access
- Centralized HR dashboard for efficient decision-making
- Significant reduction in manual processing time

---
