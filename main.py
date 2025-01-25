import pandas as pd
import requests

# Fetch data from API
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise Exception(f"Failed to fetch data from {url}")

# Load all datasets
def load_data():
    quiz_endpoint_url = "https://jsonkeeper.com/b/LLQT"
    submission_data_url = "https://api.jsonserve.com/rJvd7g"
    historical_data_url = "https://api.jsonserve.com/XgAgFJ"

    quiz_data = fetch_data(quiz_endpoint_url)
    submission_data = fetch_data(submission_data_url)
    historical_data = fetch_data(historical_data_url)

    return quiz_data, submission_data, historical_data

# Analyze student persona
def analyze_student_persona(quiz_data, submission_data, historical_data, student_id):
    student_quiz_data = quiz_data[quiz_data['student_id'] == student_id]
    student_submission_data = submission_data[submission_data['student_id'] == student_id]
    student_historical_data = historical_data[historical_data['student_id'] == student_id]

    total_quizzes = len(student_historical_data['quiz_id'].unique())
    avg_score = student_historical_data['score'].mean()

    merged_data = pd.merge(
        student_quiz_data, 
        student_submission_data, 
        on=['quiz_id', 'student_id'], 
        how='inner'
    )

    performance_by_topic = merged_data.groupby('topic').agg({
        'accuracy': 'mean',
        'difficulty': 'mean',
        'response_time': 'mean'
    }).reset_index()

    weak_topics = performance_by_topic[performance_by_topic['accuracy'] < 0.5]
    strong_topics = performance_by_topic[performance_by_topic['accuracy'] >= 0.8]

    return {
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'performance_by_topic': performance_by_topic
    }

# Generate insights
def generate_insights(persona_analysis):
    weak_topics = persona_analysis['weak_topics']['topic'].tolist()
    strong_topics = persona_analysis['strong_topics']['topic'].tolist()

    insights = []
    if weak_topics:
        insights.append(f"Focus on improving: {', '.join(weak_topics)}")
    else:
        insights.append("No weak topics detected—keep up the good work!")

    if strong_topics:
        insights.append(f"Excellent performance in: {', '.join(strong_topics)}")
    else:
        insights.append("No strong topics yet. Aim for 80%+ accuracy in specific topics.")

    return insights

# Create recommendations
def create_recommendations(persona_analysis):
    recommendations = []
    weak_topics = persona_analysis['weak_topics']
    if not weak_topics.empty:
        for _, row in weak_topics.iterrows():
            recommendations.append(
                f"Practice more questions in {row['topic']} (Difficulty Avg: {row['difficulty']:.1f})"
            )
    else:
        recommendations.append("Continue practicing to maintain your performance.")
    return recommendations

