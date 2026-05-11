"""
Main entry point for the ATS application
Run with: python run.py
"""
from app import create_app, db
from app.models import User, Candidate
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Candidate': Candidate}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
