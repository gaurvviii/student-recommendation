

import pandas as pd
from typing import Dict, List

class QuizAnalyzer:
    def __init__(self, current_quiz_data: Dict, historical_data: List[Dict]):
        self.current_quiz = pd.DataFrame(current_quiz_data)
        self.historical_data = pd.DataFrame(historical_data)
        
    def analyze_performance(self) -> Dict:
        """Analyze current and historical quiz performance"""
        return {
            'topic_analysis': self._analyze_topics(),
            'difficulty_analysis': self._analyze_difficulty_levels(),
            'trend_analysis': self._analyze_trends(),
            'weak_areas': self._identify_weak_areas()
        }
    
    def _analyze_topics(self) -> Dict:
        """Analyze performance by topic"""
        topic_performance = self.current_quiz.groupby('topic').agg({
            'correct': ['count', 'mean']
        }).round(2)
        return topic_performance.to_dict()
    
    def _analyze_difficulty_levels(self) -> Dict:
        """Analyze performance by difficulty level"""
        return self.current_quiz.groupby('difficulty').agg({
            'correct': ['count', 'mean']
        }).round(2).to_dict()
    
    def _analyze_trends(self) -> Dict:
        """Analyze performance trends over time"""
        return {
            'score_trend': self.historical_data['score'].tolist(),
            'improvement_rate': self._calculate_improvement_rate()
        }
    
    def _identify_weak_areas(self) -> List[Dict]:
        """Identify topics needing improvement"""
        weak_topics = self.current_quiz[
            self.current_quiz['correct'] == False
        ]['topic'].value_counts()
        return [{'topic': topic, 'count': count} 
                for topic, count in weak_topics.items()]
