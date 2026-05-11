"""
Chatbot Module
"""
class CandidateChatbot:
    def __init__(self, use_openai=False, openai_key=None):
        def __init__(self, use_openai=False, openai_key=None):
            self.use_openai = use_openai and openai_key
            self.faq_database = {
                "position": {
                    "keywords": ["job", "position", "role", "what", "hiring"],
                    "response": "We are hiring for the Operations Intern position. This role involves day-to-day operations management, inventory handling, and workflow process improvement."
                },
                "qualifications": {
                    "keywords": ["qualify", "requirement", "need", "eligible", "education"],
                    "response": "We're looking for freshers with MS Office proficiency, basic inventory knowledge, and excellent communication skills."
                },
                "salary": {
                    "keywords": ["salary", "pay", "stipend", "compensation", "money"],
                    "response": "The internship stipend ranges from ₹3,000 to ₹5,000 per month."
                },
                "duration": {
                    "keywords": ["duration", "long", "months", "how", "period"],
                    "response": "The internship duration is typically 3-6 months."
                },
                "benefits": {
                    "keywords": ["benefit", "perks", "advantage", "offer"],
                    "response": "Benefits include hands-on experience, certificate, and career growth opportunities."
                },
                "application": {
                    "keywords": ["apply", "application", "how", "submit", "upload"],
                    "response": "Fill the form, upload your resume, and submit. Our AI will evaluate it."
                },
                "timeline": {
                    "keywords": ["when", "timeline", "start", "date", "available"],
                    "response": "We accept applications on a rolling basis with 5-7 day interview scheduling."
                },
                "contact": {
                    "keywords": ["contact", "email", "phone", "reach", "support"],
                    "response": "Contact us at careers@netsmartz.academy"
                }
            }

    def respond(self, user_query):
        query_lower = user_query.lower()
        for category, data in self.faq_database.items():
            for keyword in data['keywords']:
                if keyword in query_lower:
                    return {'response': data['response'], 'type': 'rule_based', 'category': category}
        return {'response': "Contact HR at careers@netsmartz.academy for more info.", 'type': 'default', 'category': None}
