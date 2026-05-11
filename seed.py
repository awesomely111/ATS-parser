from app import create_app, db
from app.models import Candidate

app = create_app()

with app.app_context():

    candidates = [

        Candidate(
            name="Rahul Sharma",
            email="rahul@gmail.com",
            phone="9876543210",
            degree="BCA",
            college="Chandigarh University",
            graduation_year="2024",
            cgpa="8.2",
            tfidf_score=72.5,
            semantic_score=0,
            keyword_score=84.6,
            experience_score=80,
            education_score=100,
            overall_fit_score=81.4,
            matched_keywords="excel, communication, workflow",
            application_status="applied",
            screening_status="interview_ready",
            screening_reason="Strong profile"
        ),

        Candidate(
            name="Parvinder Singh",
            email="parvinder@gmail.com",
            phone="9988776655",
            degree="B.Tech CSE",
            college="LPU",
            graduation_year="2025",
            cgpa="7.8",
            tfidf_score=80,
            semantic_score=0,
            keyword_score=92,
            experience_score=75,
            education_score=100,
            overall_fit_score=88,
            matched_keywords="inventory management, ms office",
            application_status="applied",
            screening_status="auto_approved",
            screening_reason="Excellent profile"
        ),

        Candidate(
            name="Vanshika Arora",
            email="vanshika@gmail.com",
            phone="9871209871",
            degree="MBA",
            college="Panjab University",
            graduation_year="2023",
            cgpa="8.8",
            tfidf_score=65,
            semantic_score=0,
            keyword_score=76,
            experience_score=90,
            education_score=100,
            overall_fit_score=79,
            matched_keywords="documentation, communication",
            application_status="applied",
            screening_status="interview_ready",
            screening_reason="Good communication"
        )
    ]

    db.session.add_all(candidates)

    db.session.commit()

    print("Dummy candidates inserted successfully!")