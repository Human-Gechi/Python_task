# Zenquotes - MindFuel

## Project Overview

This project automates the delivery of motivational quotes to subscribed users via email. Built for **MindFuel**, a mental wellness startup, the platform fetches quotes from the **ZenQuotes API** and sends personalized emails to users based on their subscription preferences.

The system handles:
- Users uploads to db each day
- Email verification
- **Daily quotes** to daily subscribers at 7:00 WAT
- **Weekly quotes** to weekly subscribers every Monday at 7:00 WAT
- Logging, retries, and failure handling
- Scalable delivery for hundreds or thousands of users

---

## Features

1. **ZenQuotes API Integration**
   - Fetches a new quote every day from [ZenQuotes API](https://zenquotes.io/).
   - Handles API failures and malformed responses.

2. **User Subscription Management**
   - Users info where collected using Goolgle forms
   - Afterward, stored in a relational database (Postgres server hosted on aiven).
   - Each user has:
     - id
     - first_name
     - last_name
     - email_addresss
     - email_frequency (`Daily` or `Weekly`)
     - subscription_status (Active/Inactive)
     - email_verification_date [Date email was verified]
     - is_verified [Default False else True]

3. **Email Module**
   - Users emails are verified using Hunter.io free email verification api endpoint
   - Sends personalized quotes based on subscription type.
   - Handles delivery failures with retries.
   - Logs email delivery status per user.

4. **Logging & Monitoring**
   - Logs events to files in the parent directory:
     - Quote fetched
     - Emails sent
     - Github actions artifacts are generated after each run
     - Github actions failure email notifications if actions did not run
   - Sends summary email to admin daily with stats.

---

## Project Structure
- DE PYTHON TASK/
  - .github/
    - workflows/
      - send_emails.yml
  - Zenquotes/
    - db_conn
    - logs.py
    - Wellness.py
  - README.md


---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Human-Gechi/Python_task.git
cd DE PYTHON TASK
cd  Zenquotes
```
2. Create Virtual Environment

```bash
python -m venv python_task
python_task\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac
```

3.Install Dependencies

```bash
pip install -r requirements.txt
```
4. Create an .env file for repo secrets

## GITHUB ACTIONS WORKFLOW
The workflow is scheduled to run 7:00 AM WAT everyday and emails will be sent to users as indicated by their subscription status

**Author:** Okoli Ogechukwu Abimbola \
**Email Address:** [Email address](okoliogechi74@gmail.com)

---




