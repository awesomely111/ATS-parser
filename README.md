# AI-Powered Applicant Tracking System (ATS)

Complete Python Flask-based ATS with AI features.

## 🎯 Features
- ✅ Resume Scoring & Ranking (TF-IDF + Embeddings)
- ✅ Auto-Screening System (Automatic Filtering)
- ✅ Email AI (Outlook Integration)
- ✅ Candidate Chatbot (FAQ Support)
- ✅ HR Dashboard (Analytics & Management)

## 🚀 Installation
See QUICKSTART.md for 5-minute setup.

## 📁 Project Structure
```
ai_ats_system/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── utils/
│   │   ├── ai_scoring.py
│   │   ├── auto_screening.py
│   │   ├── chatbot.py
│   │   ├── email_service.py
│   │   └── resume_parser.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── apply.html
│   │   ├── dashboard.html
│   │   ├── candidate_detail.html
│   │   └── login.html
│   └── static/
│       └── style.css
├── data/
│   └── jd.txt
├── uploads/
├── run.py
├── .env
├── requirements.txt
├── QUICKSTART.md
└── README.md
```

## 🔧 Configuration
1. Update .env with Outlook credentials
2. Edit data/jd.txt with job description
3. Customize scoring weights in app/utils/ai_scoring.py
4. Add keywords in app/utils/ai_scoring.py

## 📊 AI Scoring
- TF-IDF Similarity: 25%
- Semantic Similarity: 20%
- Keyword Matching: 30%
- Experience: 15%
- Education: 10%

## ✨ Auto-Screening
- ≥75%: Auto-Approved
- 60-75%: Interview-Ready
- <60%: Auto-Rejected

## 📧 Outlook Integration
1. Go to Azure Portal
2. Register app
3. Get Client ID, Secret, Tenant ID
4. Update .env
5. Grant Mail permissions

## 💬 Chatbot Topics
- Position details
- Qualifications
- Salary/Stipend
- Duration
- Benefits
- Application process
- Timeline
- Contact info

## 📈 Usage

### For Candidates
1. Visit http://localhost:5000
2. Click "Apply"
3. Fill form + upload resume
4. Use chatbot for questions
5. Submit
6. AI evaluates automatically

### For HR/Admin
1. Login: admin / admin123
2. View all candidates
3. See AI scores
4. Schedule interviews
5. Export to Excel

## 🆘 Troubleshooting
See QUICKSTART.md for common issues.

## 📞 Support
Check code comments and docstrings for details.

---
**Production-ready AI ATS System** ✨
