"""
Flask Routes for ATS Application
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_login import logout_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from app import db
from app.models import User, Candidate, EmailLog, ChatMessage
from datetime import datetime
import os
import io
import pandas as pd
from groq import Groq
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from app.utils.resume_parser import extract_text_generic, extract_email, extract_phone, guess_name
from app.utils.ai_scoring import AIResumeScorer
from app.utils.auto_screening import AutoScreening
from app.utils.chatbot import CandidateChatbot
from app.utils.email_service import OutlookEmailService

# Load environment variables
load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

# Initialize blueprints
auth_bp = Blueprint('auth', __name__)
candidate_bp = Blueprint('candidate', __name__)
admin_bp = Blueprint('admin', __name__)
chatbot_bp = Blueprint('chatbot', __name__)

# ==================== AUTH ROUTES ====================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, is_admin=False)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('candidate.index'))


# ==================== CANDIDATE ROUTES ====================
@candidate_bp.route('/')
def index():
    return render_template('index.html')


@candidate_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        degree = request.form.get('degree', '')
        college = request.form.get('college', '')
        graduation_year = request.form.get('graduation_year', '')
        cgpa = request.form.get('cgpa', '')
        ms_office_skills = request.form.get('ms_office_skills', '')
        inventory_experience = request.form.get('inventory_experience', '')
        cover_letter = request.form.get('cover_letter', '')

        resume_file = request.files.get('resume')
        resume_path = None
        resume_text = ""

        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            save_name = f"{timestamp}_{filename}"
            resume_path = os.path.join(os.getenv('UPLOAD_FOLDER', 'uploads'), save_name)
            resume_file.save(resume_path)
            resume_text = extract_text_generic(resume_path)

        if resume_text:
            email = email or extract_email(resume_text) or email
            phone = phone or extract_phone(resume_text) or phone
            name = name or guess_name(resume_text, name)

        # AI Scoring
        jd_path = os.getenv('JD_PATH', 'data/jd.txt')
        ai_scores = {
            'overall_score': 0,
            'tfidf_score': 0,
            'semantic_score': 0,
            'keyword_score': 0,
            'experience_score': 0,
            'education_score': 0,
            'matched_keywords': []
        }

        if os.path.exists(jd_path):
            with open(jd_path, 'r', encoding='utf-8', errors='ignore') as f:
                jd_text = f.read()
            scorer = AIResumeScorer(jd_text)
            ai_scores = scorer.compute_overall_fit_score(resume_text)

        # Auto-screening
        screener = AutoScreening(
            min_score_for_approval=int(os.getenv('MIN_SCORE_FOR_AUTO_APPROVAL', 75)),
            min_score_for_interview=int(os.getenv('MIN_SCORE_FOR_INTERVIEW', 60))
        )
        screening_status, screening_reason = screener.auto_screen(ai_scores)

        # Create candidate
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            address=request.form.get('address', ''),
            degree=degree,
            college=college,
            graduation_year=graduation_year,
            cgpa=cgpa,
            ms_office_skills=ms_office_skills,
            inventory_experience=inventory_experience,
            cover_letter=cover_letter,
            resume_path=resume_path,
            resume_text=resume_text[:5000] if resume_text else "",
            tfidf_score=ai_scores.get('tfidf_score', 0),
            semantic_score=ai_scores.get('semantic_score', 0),
            keyword_score=ai_scores.get('keyword_score', 0),
            experience_score=ai_scores.get('experience_score', 0),
            education_score=ai_scores.get('education_score', 0),
            overall_fit_score=ai_scores.get('overall_score', 0),
            matched_keywords=', '.join(ai_scores.get('matched_keywords', [])),
            application_status='applied',
            screening_status=screening_status,
            screening_reason=screening_reason
        )

        db.session.add(candidate)
        db.session.commit()

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('candidate.index'))

    return render_template('apply.html')


# ==================== ADMIN ROUTES ====================
@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    candidates = Candidate.query.order_by(Candidate.overall_fit_score.desc()).all()
    total = len(candidates)
    auto_approved = len([c for c in candidates if c.screening_status == 'auto_approved'])
    interview_ready = len([c for c in candidates if c.screening_status == 'interview_ready'])
    auto_rejected = len([c for c in candidates if c.screening_status == 'auto_rejected'])

    stats = {
        'total': total,
        'auto_approved': auto_approved,
        'interview_ready': interview_ready,
        'auto_rejected': auto_rejected
    }

    return render_template('dashboard.html', candidates=candidates, stats=stats)

@admin_bp.route('/analytics')
def analytics():

    if not session.get('admin_logged_in'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    candidates = Candidate.query.all()

    total_applications = len(candidates)

    pending_review = len([
        c for c in candidates
        if c.screening_status == 'applied'
    ])

    interviews_scheduled = len([
        c for c in candidates
        if c.screening_status == 'interview_ready'
    ])

    accepted = len([
        c for c in candidates
        if c.screening_status == 'auto_approved'
    ])

    rejected = len([
        c for c in candidates
        if c.screening_status == 'auto_rejected'
    ])

    return render_template(
        'analytics.html',

        total_applications=total_applications,
        pending_review=pending_review,
        interviews_scheduled=interviews_scheduled,
        accepted=accepted,
        rejected=rejected
    )

@admin_bp.route('/candidate/<int:candidate_id>')
def view_candidate(candidate_id):
    if not session.get('admin_logged_in'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template('candidate_detail.html', candidate=candidate)



@admin_bp.route('/export')
def export_candidates():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403

    candidates = Candidate.query.all()
    data = []

    for c in candidates:
        data.append({
            'Name': c.name,
            'Email': c.email,
            'Phone': c.phone,
            'Overall Score': f"{c.overall_fit_score:.1f}",
            'TF-IDF': f"{c.tfidf_score:.1f}",
            'Keywords': f"{c.keyword_score:.1f}",
            'Status': c.screening_status
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Candidates')

    output.seek(0)
    return send_file(
        output,
        download_name=f'candidates_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# ==================== CHATBOT ROUTES ====================
# @chatbot_bp.route('/api/chat', methods=['POST'])
@chatbot_bp.route('/ai-chatbot')
def chat_page():
    return render_template('chatbot.html')
# ==================== CHATBOT ROUTES ====================

def keyword_match_score(resume_text, jd_text):

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())

    matched_words = resume_words.intersection(jd_words)

    if len(jd_words) == 0:
        return 0, []

    score = (len(matched_words) / len(jd_words)) * 100

    return round(score, 2), list(matched_words)


def semantic_similarity_score(resume_text, jd_text):

    emb1 = embedding_model.encode([resume_text])

    emb2 = embedding_model.encode([jd_text])

    similarity = cosine_similarity(emb1, emb2)[0][0]

    return round(similarity * 100, 2)

@chatbot_bp.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():

    try:

        resume_file = request.files.get('resume')

        jd_text = request.form.get('jd')

        if not resume_file:
            return jsonify({
                "error": "Resume file missing"
            }), 400

        if not jd_text:
            return jsonify({
                "error": "Job description missing"
            }), 400

        # SAVE FILE

        filename = secure_filename(resume_file.filename)

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

        save_name = f"{timestamp}_{filename}"

        resume_path = os.path.join(
            os.getenv('UPLOAD_FOLDER', 'uploads'),
            save_name
        )

        resume_file.save(resume_path)

        # EXTRACT TEXT

        resume_text = extract_text_generic(resume_path)

        # STORE SESSION MEMORY

        session['resume_text'] = resume_text[:10000]

        session['jd_text'] = jd_text[:5000]

        session['conversation_history'] = []

        # CALCULATE SCORES

        keyword_score, matched_keywords = keyword_match_score(
            resume_text,
            jd_text
        )

        semantic_score = semantic_similarity_score(
            resume_text,
            jd_text
        )

        final_score = round(
            (keyword_score * 0.4) +
            (semantic_score * 0.6),
            2
        )

        # AI ANALYSIS

        prompt = f"""
        Resume:
        {resume_text}

        Job Description:
        {jd_text}

        Analyze this candidate and provide:

        1. ATS Match Score
        2. Missing Skills
        3. Resume Improvements
        4. Interview Questions
        """

        completion = client.chat.completions.create(

           model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ATS recruiter."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.5,
            max_tokens=1000
        )

        ai_response = completion.choices[0].message.content

        return jsonify({

            "success": True,

            "keyword_score": keyword_score,

            "semantic_score": semantic_score,

            "final_ats_score": final_score,

            "matched_keywords": matched_keywords[:20],

            "ai_analysis": ai_response

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@chatbot_bp.route('/api/ai-chat', methods=['POST'])
def ai_chat():

    try:

        data = request.get_json()

        user_message = data.get("message", "")

        if not user_message:
            return jsonify({
                "error": "Message required"
            }), 400

        resume_text = session.get('resume_text', '')

        jd_text = session.get('jd_text', '')

        conversation_history = session.get(
            'conversation_history',
            []
        )

        system_prompt = f"""
        You are an advanced AI recruitment assistant.

        Always format responses professionally using:

        - Headings
        - Bullet points
        - Short paragraphs
        - Numbered lists
        - Proper spacing
        - Emojis where useful

        Never return one large paragraph.

        Keep responses visually clean and modern.

        Resume:
        {resume_text}

        Job Description:
        {jd_text}

        You help with:
        - ATS score analysis
        - Resume improvement
        - Missing skills
        - Interview preparation
        - Career guidance
        - Resume rewriting
        - Project suggestions
        """

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(conversation_history)

        messages.append({
            "role": "user",
            "content": user_message
        })

        completion = client.chat.completions.create(

           model="llama-3.3-70b-versatile",

            messages=messages,

            temperature=0.7,

            max_tokens=700
        )

        bot_response = completion.choices[0].message.content

        # SAVE MEMORY

        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        conversation_history.append({
            "role": "assistant",
            "content": bot_response
        })

        session['conversation_history'] = conversation_history

        # SAVE DB CHAT

        chat_msg = ChatMessage(
            user_query=user_message,
            bot_response=bot_response,
            response_type='ai_chat'
        )

        db.session.add(chat_msg)
        db.session.commit()

        return jsonify({
            "response": bot_response
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

@admin_bp.route('/delete-candidate/<int:candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):

    try:

        candidate = Candidate.query.get(candidate_id)

        if not candidate:
            return jsonify({
                "success": False,
                "message": "Candidate not found"
            }), 404

        db.session.delete(candidate)

        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:

        db.session.rollback()

        print("DELETE ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
# routes/chatbot.py

# from flask import Blueprint, render_template

# chatbot = Blueprint('chatbot', __name__)

# @chatbot.route('/ai-chatbot')
# def chat_page():
#     return render_template('chatbot/chat.html')

# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are an AI recruitment assistant."
#         },
#         {
#             "role": "user",
#             "content": 'hello'
#         }
#     ]
# )

# bot_response = completion.choices[0].message.content


# from flask import Blueprint, render_template, request, jsonify
# # from openai import OpenAI

# # OpenAI Client

# chatbot = Blueprint('chatbot', __name__)
# """
# Flask Routes for ATS Application
# """
# from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
# from flask_login import login_required, current_user, login_user, logout_user
# from werkzeug.utils import secure_filename
# from app import db
# from app.models import User, Candidate, EmailLog, ChatMessage
# from datetime import datetime
# import os
# import io
# import pandas as pd

# from app.utils.resume_parser import extract_text_generic, extract_email, extract_phone, guess_name
# from app.utils.ai_scoring import AIResumeScorer
# from app.utils.auto_screening import AutoScreening
# from app.utils.chatbot import CandidateChatbot
# from app.utils.email_service import OutlookEmailService

# # Initialize blueprints
# auth_bp = Blueprint('auth', __name__)
# candidate_bp = Blueprint('candidate', __name__)
# admin_bp = Blueprint('admin', __name__)
# chatbot_bp = Blueprint('chatbot', __name__)

# # ==================== AUTH ROUTES ====================
# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         email = request.form.get('email')

#         if User.query.filter_by(username=username).first():
#             flash('Username already exists', 'danger')
#             return redirect(url_for('auth.register'))

#         user = User(username=username, email=email, is_admin=False)
#         user.set_password(password)
#         db.session.add(user)
#         db.session.commit()

#         flash('Registration successful! Please login.', 'success')
#         return redirect(url_for('auth.login'))

#     return render_template('register.html')

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = User.query.filter_by(username=username).first()

#         if user and user.check_password(password):
#             login_user(user)
#             return redirect(url_for('admin.dashboard'))
#         else:
#             flash('Invalid username or password', 'danger')

#     return render_template('login.html')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('candidate.index'))

# # ==================== CANDIDATE ROUTES ====================
# @candidate_bp.route('/')
# def index():
#     return render_template('index.html')

# @candidate_bp.route('/apply', methods=['GET', 'POST'])
# def apply():
#     if request.method == 'POST':
#         name = request.form.get('name', '')
#         email = request.form.get('email', '')
#         phone = request.form.get('phone', '')
#         degree = request.form.get('degree', '')
#         college = request.form.get('college', '')
#         graduation_year = request.form.get('graduation_year', '')
#         cgpa = request.form.get('cgpa', '')
#         ms_office_skills = request.form.get('ms_office_skills', '')
#         inventory_experience = request.form.get('inventory_experience', '')
#         cover_letter = request.form.get('cover_letter', '')

#         resume_file = request.files.get('resume')
#         resume_path = None
#         resume_text = ""

#         if resume_file and resume_file.filename:
#             filename = secure_filename(resume_file.filename)
#             timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
#             save_name = f"{timestamp}_{filename}"
#             resume_path = os.path.join(os.getenv('UPLOAD_FOLDER', 'uploads'), save_name)
#             resume_file.save(resume_path)
#             resume_text = extract_text_generic(resume_path)

#         if resume_text:
#             email = email or extract_email(resume_text) or email
#             phone = phone or extract_phone(resume_text) or phone
#             name = name or guess_name(resume_text, name)

#         # AI Scoring
#         jd_path = os.getenv('JD_PATH', 'data/jd.txt')
#         ai_scores = {
#             'overall_score': 0,
#             'tfidf_score': 0,
#             'semantic_score': 0,
#             'keyword_score': 0,
#             'experience_score': 0,
#             'education_score': 0,
#             'matched_keywords': []
#         }

#         if os.path.exists(jd_path):
#             with open(jd_path, 'r', encoding='utf-8', errors='ignore') as f:
#                 jd_text = f.read()
#             scorer = AIResumeScorer(jd_text)
#             ai_scores = scorer.compute_overall_fit_score(resume_text)

#         # Auto-screening
#         screener = AutoScreening(
#             min_score_for_approval=int(os.getenv('MIN_SCORE_FOR_AUTO_APPROVAL', 75)),
#             min_score_for_interview=int(os.getenv('MIN_SCORE_FOR_INTERVIEW', 60))
#         )
#         screening_status, screening_reason = screener.auto_screen(ai_scores)

#         # Create candidate
#         candidate = Candidate(
#             name=name,
#             email=email,
#             phone=phone,
#             address=request.form.get('address', ''),
#             degree=degree,
#             college=college,
#             graduation_year=graduation_year,
#             cgpa=cgpa,
#             ms_office_skills=ms_office_skills,
#             inventory_experience=inventory_experience,
#             cover_letter=cover_letter,
#             resume_path=resume_path,
#             resume_text=resume_text[:5000] if resume_text else "",
#             tfidf_score=ai_scores.get('tfidf_score', 0),
#             semantic_score=ai_scores.get('semantic_score', 0),
#             keyword_score=ai_scores.get('keyword_score', 0),
#             experience_score=ai_scores.get('experience_score', 0),
#             education_score=ai_scores.get('education_score', 0),
#             overall_fit_score=ai_scores.get('overall_score', 0),
#             matched_keywords=', '.join(ai_scores.get('matched_keywords', [])),
#             application_status='applied',
#             screening_status=screening_status,
#             screening_reason=screening_reason
#         )

#         db.session.add(candidate)
#         db.session.commit()

#         flash('Application submitted successfully!', 'success')
#         return redirect(url_for('candidate.index'))

#     return render_template('apply.html')

# # ==================== ADMIN ROUTES ====================
# @admin_bp.route('/dashboard')
# @login_required
# def dashboard():
#     if not current_user.is_admin:
#         flash('Access denied', 'danger')
#         return redirect(url_for('candidate.index'))

#     candidates = Candidate.query.order_by(Candidate.overall_fit_score.desc()).all()
#     total = len(candidates)
#     auto_approved = len([c for c in candidates if c.screening_status == 'auto_approved'])
#     interview_ready = len([c for c in candidates if c.screening_status == 'interview_ready'])
#     auto_rejected = len([c for c in candidates if c.screening_status == 'auto_rejected'])

#     stats = {
#         'total': total,
#         'auto_approved': auto_approved,
#         'interview_ready': interview_ready,
#         'auto_rejected': auto_rejected
#     }

#     return render_template('dashboard.html', candidates=candidates, stats=stats)

# @admin_bp.route('/candidate/<int:candidate_id>')
# @login_required
# def view_candidate(candidate_id):
#     if not current_user.is_admin:
#         flash('Access denied', 'danger')
#         return redirect(url_for('candidate.index'))

#     candidate = Candidate.query.get_or_404(candidate_id)
#     return render_template('candidate_detail.html', candidate=candidate)

# @admin_bp.route('/export')
# @login_required
# def export_candidates():
#     if not current_user.is_admin:
#         return jsonify({'error': 'Unauthorized'}), 403

#     candidates = Candidate.query.all()
#     data = []

#     for c in candidates:
#         data.append({
#             'Name': c.name,
#             'Email': c.email,
#             'Phone': c.phone,
#             'Overall Score': f"{c.overall_fit_score:.1f}",
#             'TF-IDF': f"{c.tfidf_score:.1f}",
#             'Keywords': f"{c.keyword_score:.1f}",
#             'Status': c.screening_status
#         })

#     df = pd.DataFrame(data)
#     output = io.BytesIO()

#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Candidates')

#     output.seek(0)
#     return send_file(
#         output,
#         download_name=f'candidates_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
#         as_attachment=True,
#         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )

# # ==================== CHATBOT ROUTES ====================
# @chatbot_bp.route('/api/chat', methods=['POST'])
# def chatbot_response():
#     user_query = request.json.get('query', '')

#     if not user_query:
#         return jsonify({'error': 'Empty query'}), 400

#     chatbot = CandidateChatbot()
#     response = chatbot.respond(user_query)

#     chat_msg = ChatMessage(
#         user_query=user_query,
#         bot_response=response['response'],
#         response_type=response['type']
#     )
#     db.session.add(chat_msg)
#     db.session.commit()

#     return jsonify(response)
# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )

# @chatbot_bp.route('/api/ai-chat', methods=['POST'])
# def ai_chat():

#     data = request.get_json()

#     user_message = data.get("message", "")

#     if not user_message:
#         return jsonify({"error": "Message required"}), 400

#     try:

#         completion = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are an AI recruitment assistant."
#                 },
#                 {
#                     "role": "user",
#                     "content": user_message
#                 }
#             ],
#             temperature=0.7,
#             max_tokens=500
#         )

#         bot_response = completion.choices[0].message.content

#         return jsonify({
#             "response": bot_response
#         })

#     except Exception as e:
#         return jsonify({
#             "error": str(e)
#         }), 500