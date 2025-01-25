import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class PerformanceMetrics:
    accuracy: float
    score: float
    correct_answers: int
    incorrect_answers: int
    total_questions: int
    duration: str
    topic: str
    quiz_title: str
    submission_date: datetime

class PerformanceAnalyzer:
    def __init__(self):
        self.quiz_data = None
        self.submission_data = None
        self.historical_data = None
        self.performance_df = None

    def load_data(self) -> bool:
        """Load all required data files."""
        try:
            with open('data/quiz_data.json', 'r') as f:
                self.quiz_data = json.load(f)
            
            with open('data/submission_data.json', 'r') as f:
                self.submission_data = json.load(f)
                if isinstance(self.submission_data, dict):
                    self.submission_data = self.submission_data.get('submissions', [])
            
            with open('data/historical_data.json', 'r') as f:
                self.historical_data = json.load(f)
            
            return True
        except FileNotFoundError as e:
            print(f"Error loading data files: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON data: {e}")
            return False

    def process_submission(self, submission: Dict) -> Optional[PerformanceMetrics]:
        """Process a single submission and return metrics."""
        try:
            return PerformanceMetrics(
                accuracy=float(submission['accuracy']),
                score=float(submission['final_score']),
                correct_answers=int(submission['correct_answers']),
                incorrect_answers=int(submission['incorrect_answers']),
                total_questions=int(submission['total_questions']),
                duration=submission.get('duration', '00:00'),
                topic=submission['quiz_topic'],
                quiz_title=submission['quiz_title'],
                submission_date=datetime.fromisoformat(submission['submitted_at'])
            )
        except (KeyError, ValueError) as e:
            print(f"Error processing submission: {e}")
            return None

    def analyze_submissions(self) -> pd.DataFrame:
        """Process all submissions and convert to DataFrame."""
        if not self.submission_data:
            print("No submission data available")
            return pd.DataFrame()

        processed_data = []
        for submission in self.submission_data:
            if not isinstance(submission, dict):
                continue
                
            metrics = self.process_submission(submission)
            if metrics:
                processed_data.append({
                    'student_id': submission.get('user_id'),
                    'quiz_title': metrics.quiz_title,
                    'topic': metrics.topic,
                    'accuracy': metrics.accuracy,
                    'score': metrics.score,
                    'correct_answers': metrics.correct_answers,
                    'incorrect_answers': metrics.incorrect_answers,
                    'total_questions': metrics.total_questions,
                    'duration': metrics.duration,
                    'submission_date': metrics.submission_date
                })
        
        self.performance_df = pd.DataFrame(processed_data)
        return self.performance_df

    def analyze_topic_performance(self) -> Optional[pd.DataFrame]:
        """Analyze performance by topic."""
        if self.performance_df is None or self.performance_df.empty:
            print("No performance data available")
            return None

        try:
            topic_metrics = self.performance_df.groupby('topic').agg({
                'accuracy': ['mean', 'std', 'count'],
                'score': ['mean', 'std'],
                'correct_answers': 'sum',
                'incorrect_answers': 'sum',
                'total_questions': 'sum'
            }).round(2)

            # Flatten column names
            topic_metrics.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] 
                                   for col in topic_metrics.columns]
            return topic_metrics.reset_index()
        except Exception as e:
            print(f"Error analyzing topic performance: {e}")
            return None

    def plot_performance_trends(self):
        """Generate performance visualization plots."""
        if self.performance_df is None or self.performance_df.empty:
            print("No data available for plotting")
            return

        try:
            plt.style.use('seaborn')
            fig = plt.figure(figsize=(15, 10))

            # Plot 1: Topic Performance
            ax1 = fig.add_subplot(221)
            topic_perf = self.performance_df.groupby('topic')['accuracy'].mean().sort_values()
            topic_perf.plot(kind='barh', ax=ax1)
            ax1.set_title('Average Accuracy by Topic')
            ax1.set_xlabel('Accuracy (%)')

            # Plot 2: Time Series Trend
            ax2 = fig.add_subplot(222)
            time_trend = self.performance_df.set_index('submission_date')['accuracy'].rolling('7D').mean()
            time_trend.plot(ax=ax2)
            ax2.set_title('7-Day Rolling Average Accuracy')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Accuracy (%)')

            # Plot 3: Question Distribution
            ax3 = fig.add_subplot(223)
            self.performance_df['correct_ratio'] = (
                self.performance_df['correct_answers'] / self.performance_df['total_questions']
            )
            self.performance_df['correct_ratio'].hist(ax=ax3, bins=20)
            ax3.set_title('Distribution of Correct Answer Ratios')
            ax3.set_xlabel('Correct Answer Ratio')
            ax3.set_ylabel('Frequency')

            # Plot 4: Topic Progress
            ax4 = fig.add_subplot(224)
            topic_progress = self.performance_df.pivot_table(
                index='submission_date',
                columns='topic',
                values='accuracy',
                aggfunc='mean'
            ).rolling('7D').mean()
            topic_progress.plot(ax=ax4)
            ax4.set_title('Topic Progress Over Time')
            ax4.set_xlabel('Date')
            ax4.set_ylabel('Accuracy (%)')

            plt.tight_layout()
            plt.savefig('performance_analysis.png')
            plt.close()

        except Exception as e:
            print(f"Error generating plots: {e}")

    def generate_insights(self) -> List[str]:
        """Generate insights from the performance data."""
        if self.performance_df is None or self.performance_df.empty:
            return ["No data available for analysis"]

        insights = []
        try:
            # Overall performance
            avg_accuracy = self.performance_df['accuracy'].mean()
            total_questions = self.performance_df['total_questions'].sum()
            insights.append(f"Overall Performance Summary:")
            insights.append(f"• Average Accuracy: {avg_accuracy:.1f}%")
            insights.append(f"• Total Questions Attempted: {total_questions}")

            # Topic analysis
            topic_metrics = self.analyze_topic_performance()
            if topic_metrics is not None:
                insights.append("\nTopic Analysis:")
                for _, row in topic_metrics.iterrows():
                    insights.append(
                        f"• {row['topic']}:"
                        f" Accuracy {row['accuracy_mean']:.1f}% (±{row['accuracy_std']:.1f}%),"
                        f" {row['accuracy_count']} attempts"
                    )

            # Trend analysis
            recent_trend = self.performance_df.sort_values('submission_date').tail(5)['accuracy'].mean()
            overall_mean = self.performance_df['accuracy'].mean()
            trend_diff = recent_trend - overall_mean
            
            insights.append("\nRecent Performance Trend:")
            if abs(trend_diff) > 5:
                direction = "improving" if trend_diff > 0 else "declining"
                insights.append(f"• Performance is {direction} ({trend_diff:+.1f}% vs overall average)")
            else:
                insights.append("• Performance is stable")

        except Exception as e:
            insights.append(f"Error generating insights: {e}")

        return insights

def main():
    """Main execution function."""
    analyzer = PerformanceAnalyzer()
    
    # Load and process data
    if not analyzer.load_data():
        print("Failed to load required data")
        return

    # Analyze submissions
    analyzer.analyze_submissions()
    
    # Generate visualizations
    analyzer.plot_performance_trends()
    
    # Generate and print insights
    insights = analyzer.generate_insights()
    print("\nPerformance Insights:")
    for insight in insights:
        print(insight)

if __name__ == "__main__":
    main()