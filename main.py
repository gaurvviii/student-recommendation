import json
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the quiz and submission data
def load_data():
    with open('data/quiz_data.json', 'r') as f:
        quiz_data = json.load(f)
    
    with open('data/submission_data.json', 'r') as f:
        submission_data = json.load(f)
    
    # Debugging: Check the type of submission_data
    print(f"Type of submission_data: {type(submission_data)}")
    if isinstance(submission_data, dict):  # If it's a dictionary, check if it contains the list under a key
        submission_data = submission_data.get('submissions', [])
    
    with open('data/Historical_data.json', 'r') as f:
        historical_data = json.load(f)
    
    return quiz_data, submission_data, historical_data

# Step 2: Process Data and Analyze Student Performance
def process_submission_data(submission_data):
    student_performance = []
    for submission in submission_data:
        # Check if submission is a dictionary
        if isinstance(submission, dict):
            student_id = submission['user_id']
            quiz_title = submission['quiz_title']  # Direct access as per the new format
            accuracy = submission['accuracy'] if isinstance(submission['accuracy'], float) else float(submission['accuracy'])
            final_score = float(submission['final_score'])
            correct_answers = submission['correct_answers']
            incorrect_answers = submission['incorrect_answers']
            topic = submission['quiz_topic']  
            question_count = submission['total_questions']

            student_performance.append({
                'student_id': student_id,
                'quiz_title': quiz_title,
                'accuracy': accuracy,
                'final_score': final_score,
                'correct_answers': correct_answers,
                'incorrect_answers': incorrect_answers,
                'topic': topic,
                'question_count': question_count
            })
        else:
            print(f"Skipping non-dictionary entry: {submission}")
    
    performance_df = pd.DataFrame(student_performance)
    return performance_df

# Step 3: Analyze Student Performance
def analyze_performance(performance_df):
    print(f"Columns in performance_df: {performance_df.columns.tolist()}")

    # Performance by topic
    if 'topic' in performance_df.columns:
        topic_performance = performance_df.groupby('topic').agg({
            'accuracy': ['mean', 'std'],
            'final_score': 'mean',
            'correct_answers': 'sum',
            'incorrect_answers': 'sum',
            'question_count': 'mean'
        }).reset_index()
        print("Performance by Topic:\n", topic_performance)

        # Plot performance by topics
        plt.figure(figsize=(10, 6))
        plt.bar(topic_performance['topic'], topic_performance[('accuracy', 'mean')], color='blue', alpha=0.7)
        plt.xlabel('Topic')
        plt.ylabel('Average Accuracy (%)')
        plt.title('Average Accuracy by Topic')
        plt.xticks(rotation=90)
        plt.show(block=False)


        return topic_performance
    else:
        print("No 'topic' column found in the performance data.")
        return None

# Step 4: Analyze User's Performance and Generate Insights
def analyze_user_performance(user_id, performance_df):
    # Filter the data for the given user
    user_data = performance_df[performance_df['student_id'] == user_id]
    
    # Weak areas: Identify topics with low accuracy
    weak_areas = user_data.groupby('topic')['accuracy'].mean().sort_values().head(3)
    
    # Improvement trends: Compare accuracy over time (or across quizzes)
    improvement_trends = user_data.groupby('quiz_title')['accuracy'].mean().sort_values(ascending=False)
    
    # Performance gaps: Compare the user's performance with the overall mean performance by topic
    overall_performance_by_topic = performance_df.groupby('topic')['accuracy'].mean()
    user_performance_by_topic = user_data.groupby('topic')['accuracy'].mean()
    performance_gap = overall_performance_by_topic - user_performance_by_topic
    
    return weak_areas, improvement_trends, performance_gap

# Step 5: Generate Recommendations based on the analysis
def generate_recommendations(user_id, performance_df):
    weak_areas, improvement_trends, performance_gap = analyze_user_performance(user_id, performance_df)
    
    recommendations = []
    
    # Recommend topics for improvement
    recommendations.append("Focus on the following weak areas:")
    for topic in weak_areas.index:
        recommendations.append(f"  - {topic} (Accuracy: {weak_areas[topic]:.2f}%)")
    
    # Suggest additional practice on specific question types or levels
    recommendations.append("\nRecommended next steps for improvement:")
    if len(weak_areas) > 0:
        recommendations.append("  - Practice more questions on the identified weak topics.")
    else:
        recommendations.append("  - Keep maintaining a consistent practice routine.")
    
    # Suggest a balanced approach to difficulty
    recommendations.append("\nSuggested difficulty levels:")
    if len(improvement_trends) > 0:
        recommendations.append(f"  - Focus on intermediate-level questions for better mastery.")
        recommendations.append(f"  - Gradually try more difficult quizzes once you improve in the basics.")
    
    return recommendations

# Main function to run the analysis
def main():
    # Load data
    quiz_data, submission_data, historical_data = load_data()

    # Process data
    performance_df = process_submission_data(submission_data)

    # Analyze performance
    if performance_df is not None:
        topic_performance = analyze_performance(performance_df)
        if topic_performance is not None:
            # Perform further analysis
            pass
        else:
            print("Unable to analyze performance due to missing 'topic' column.")
    
    # Example: Generate recommendations for a specific user (replace with user_id from your data)
    user_id = "7ZXdz3zHuNcdg9agb5YpaOGLQqw2"  
    recommendations = generate_recommendations(user_id, performance_df)
    
    print("\nRecommendations for improvement:")
    for rec in recommendations:
        print(rec)

if __name__ == "__main__":
    main()
