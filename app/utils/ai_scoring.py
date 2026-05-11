"""
AI Resume Scoring Module
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class AIResumeScorer:
    def __init__(self, jd_text=None):
        self.jd_text = jd_text
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=100, ngram_range=(1, 2))
        self.keywords_map = {
            "Operations Intern": [
                "ms office", "excel", "word", "powerpoint",
                "inventory management", "operations", "process improvement",
                "documentation", "coordination", "communication",
                "administrative", "workflow", "efficiency"
            ]
        }

    def compute_tfidf_score(self, resume_text):
        if not self.jd_text:
            return 0
        try:
            tfidf = self.tfidf_vectorizer.fit_transform([self.jd_text, resume_text])
            similarity = cosine_similarity(tfidf[0], tfidf[1])[0][0]
            return float(similarity * 100)
        except:
            return 0

    def compute_keyword_score(self, resume_text, position="Operations Intern"):
        keywords = self.keywords_map.get(position, [])
        matched_keywords = []
        resume_lower = resume_text.lower()
        for keyword in keywords:
            if keyword.lower() in resume_lower:
                matched_keywords.append(keyword)
        if not keywords:
            return 0, []
        score = (len(matched_keywords) / len(keywords)) * 100
        return float(score), matched_keywords

    def compute_experience_score(self, resume_text, required_years=0):
        patterns = [r'(\d+)\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)', r'(?:experience|exp):\s*(\d+)\s*(?:years?|yrs?)']
        for pattern in patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                return 100 if years == 0 else 80
        return 50

    def compute_education_score(self, resume_text, required_degrees=[
    "bachelor",
    "master",
    "mtech",
    "mba",
    "b.tech",
    "btech",
    "bca",
    "b.sc",
    "bsc",
    "mca"
]):
        resume_lower = resume_text.lower()
        for degree in required_degrees:
            if degree.lower() in resume_lower:
                return 100
        return 50

    # def compute_overall_fit_score(self, resume_text, weights=None):
    #     if weights is None:
    #         weights = {'tfidf': 0.25, 'semantic': 0.20, 'keywords': 0.30, 'experience': 0.15, 'education': 0.10}

    #     scores = {}
    #     scores['tfidf'] = self.compute_tfidf_score(resume_text)
    #     kw_score, keywords = self.compute_keyword_score(resume_text)
    #     scores['keywords'] = kw_score
    #     scores['experience'] = self.compute_experience_score(resume_text, required_years=0)
    #     scores['education'] = self.compute_education_score(resume_text)
    #     scores['semantic'] = 0

    #     overall_score = sum(scores[key] * weights[key] for key in scores)

    #     return {
    #         'overall_score': float(overall_score),
    #         'tfidf_score': scores['tfidf'],
    #         'semantic_score': scores['semantic'],
    #         'keyword_score': scores['keywords'],
    #         'experience_score': scores['experience'],
    #         'education_score': scores['education'],
    #         'matched_keywords': keywords
    #     }

    def compute_overall_fit_score(self, resume_text, weights=None):

        if weights is None:

            weights = {
                'tfidf': 0.30,
                'keywords': 0.40,
                'experience': 0.15,
                'education': 0.15
            }

        scores = {}

        scores['tfidf'] = self.compute_tfidf_score(resume_text)

        kw_score, keywords = self.compute_keyword_score(resume_text)

        scores['keywords'] = kw_score

        scores['experience'] = self.compute_experience_score(
            resume_text,
            required_years=0
        )

        scores['education'] = self.compute_education_score(
            resume_text
        )

        overall_score = (
            scores['tfidf'] * weights['tfidf'] +
            scores['keywords'] * weights['keywords'] +
            scores['experience'] * weights['experience'] +
            scores['education'] * weights['education']
        )

        # Fresher boost

        if scores['keywords'] >= 70:
            overall_score += 10

        overall_score = min(overall_score, 100)

        return {
            'overall_score': float(overall_score),
            'tfidf_score': scores['tfidf'],
            'semantic_score': 0,
            'keyword_score': scores['keywords'],
            'experience_score': scores['experience'],
            'education_score': scores['education'],
            'matched_keywords': keywords
        }