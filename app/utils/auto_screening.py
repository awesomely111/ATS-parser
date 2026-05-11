"""
Auto-Screening Module
"""
class AutoScreening:
    def __init__(self, min_score_for_approval=75, min_score_for_interview=60):
        self.min_score_for_approval = min_score_for_approval
        self.min_score_for_interview = min_score_for_interview

    def auto_screen(self, ai_scores):
        overall_score = ai_scores.get('overall_score', 0)
        if overall_score >= self.min_score_for_approval:
            return 'auto_approved', 'Auto-approved by AI system'
        elif overall_score >= self.min_score_for_interview:
            return 'interview_ready', 'Recommended for interview'
        else:
            return 'auto_rejected', f'Score below threshold ({overall_score:.1f}%)'
