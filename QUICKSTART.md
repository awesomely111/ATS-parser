# QUICK START - AI ATS (5 Minutes)

## Setup Steps

### 1. Extract & Navigate
```bash
unzip AI_ATS_COMPLETE_SYSTEM.zip
cd ai_ats_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Configure .env
Edit .env file with your Outlook credentials:
- MICROSOFT_CLIENT_ID
- MICROSOFT_CLIENT_SECRET
- MICROSOFT_TENANT_ID
- OUTLOOK_EMAIL

### 5. Run Application
```bash
python run.py
```

### 6. Access
- **Homepage**: http://localhost:5000
- **Apply**: http://localhost:5000/apply
- **Dashboard**: http://localhost:5000/dashboard
- **Admin Login**: admin / admin123

## Features
✓ Resume Scoring (AI)
✓ Auto-Screening
✓ Email AI (Outlook)
✓ Chatbot
✓ HR Dashboard

## Troubleshooting
- Port in use? Edit run.py and change port
- Dependencies issue? Run: pip install --upgrade pip
- Resume parsing issue? Ensure uploads/ folder exists
- AI scores zero? Update data/jd.txt with job description

For full documentation, see README.md
