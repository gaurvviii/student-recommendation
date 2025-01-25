import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Step 1: Load the quiz and submission data
def load_data():
    with open('quiz_data.json', 'r') as f:
        quiz_data = json.load(f)
    
    with open('quiz_submission_data.json', 'r') as f:
        submission_data = json.load(f)
    
    return quiz_data, submission_data

# Step 2: Process Data and Analyze Student Performance
def process_submission_data(submission_data):
    student_performance = []
    for submission in submission_data:
        student_id = submission['user_id']
        quiz_title = submission['quiz']['title']
        accuracy = float(submission['accuracy'].strip('%'))
        total_score = submission['final_score']
        correct_answers = submission['correct_answers']
        incorrect_answers = submission['incorrect_answers']
        topics = submission['quiz']['topic']
        question_count = submission['total_questions']
        
        student_performance.append({
            'student_id': student_id,
            'quiz_title': quiz_title,
            'accuracy': accuracy,
            'total_score': total_score,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'topics': topics,
            'question_count': question_count
        })
    
    performance_df = pd.DataFrame(student_performance)
    return performance_df

# Step 3: Analyze Student Performance
def analyze_performance(performance_df):
    # Performance by topic
    topic_performance = performance_df.groupby('topics').agg({
        'accuracy': ['mean', 'std'],
        'total_score': 'mean',
        'correct_answers': 'sum',
        'incorrect_answers': 'sum',
        'question_count': 'mean'
    }).reset_index()

    print("Performance by Topic:\n", topic_performance)

    # Plot performance by topics
    plt.figure(figsize=(10, 6))
    plt.bar(topic_performance['topics'], topic_performance[('accuracy', 'mean')], color='blue', alpha=0.7)
    plt.xlabel('Topic')
    plt.ylabel('Average Accuracy (%)')
    plt.title('Average Accuracy by Topic')
    plt.xticks(rotation=90)
    plt.show()

    return topic_performance

# Step 4: Identify Weak Areas and Performance Gaps
def identify_weak_areas(performance_df, topic_performance):
    # Weak areas based on accuracy per topic
    weak_areas = topic_performance[topic_performance[('accuracy', 'mean')] < 70]  # Topics with <70% accuracy
    print("\nWeak Areas (accuracy < 70%):\n", weak_areas)

    # Highlighting students who are struggling
    students_struggling = performance_df[performance_df['accuracy'] < 60]
    print("\nStudents Struggling (accuracy < 60%):\n", students_struggling[['student_id', 'quiz_title', 'accuracy']])

    return weak_areas, students_struggling

# Step 5: Generate Recommendations
def generate_recommendations(student_id, performance_df, weak_areas):
    # Suggest improvement topics
    student_data = performance_df[performance_df['student_id'] == student_id]
    weak_topics = student_data.groupby('topics').agg({
        'accuracy': 'mean',
        'incorrect_answers': 'sum'
    }).reset_index()

    weak_topics = weak_topics[weak_topics['accuracy'] < 60]
    suggestions = weak_topics[['topics', 'accuracy']]
    
    if not suggestions.empty:
        print(f"\nSuggested Topics for Improvement for Student {student_id}:")
        print(suggestions)
    else:
        print(f"\nStudent {student_id} is performing well.")
    
    # Class-wide suggestions for improvement
    top_3_topics_for_improvement = weak_areas.sort_values(by=('accuracy', 'mean')).head(3)
    print("\nClass-Wide Suggested Topics for Improvement:\n", top_3_topics_for_improvement)

# Step 6: Define Student Persona Based on Performance
def define_student_persona(student_id, performance_df):
    student_data = performance_df[performance_df['student_id'] == student_id]
    avg_accuracy = student_data['accuracy'].mean()
    avg_score = student_data['total_score'].mean()

    if avg_accuracy > 85 and avg_score > 90:
        return "Top Performer"
    elif avg_accuracy < 60:
        return "Needs Improvement"
    else:
        return "Average Performer"

# Step 7: Visualize Overall Performance Insights
def visualize_class_performance(performance_df):
    # Class-level insights
    class_performance = performance_df.groupby('topics').agg({
        'accuracy': 'mean',
        'total_score': 'mean',
        'correct_answers': 'sum',
        'incorrect_answers': 'sum'
    }).reset_index()

    # Visualize class-wide accuracy trends
    plt.figure(figsize=(10, 6))
    plt.bar(class_performance['topics'], class_performance['accuracy'], color='green', alpha=0.7)
    plt.xlabel('Topic')
    plt.ylabel('Class Average Accuracy (%)')
    plt.title('Class Average Accuracy by Topic')
    plt.xticks(rotation=90)
    plt.show()

    return class_performance

# Main function to run the analysis
def main():
    # Load data
    quiz_data, submission_data = load_data()

    # Process data
    performance_df = process_submission_data(submission_data)

    # Analyze performance
    topic_performance = analyze_performance(performance_df)

    # Identify weak areas
    weak_areas, students_struggling = identify_weak_areas(performance_df, topic_performance)

    # Generate recommendations for a specific student (example: student ID 'YcDFSO4ZukTJnnFMgRNVwZTE4j42')
    student_id = 'YcDFSO4ZukTJnnFMgRNVwZTE4j42'
    generate_recommendations(student_id, performance_df, weak_areas)

    # Define student persona
    persona = define_student_persona(student_id, performance_df)
    print(f"\nStudent Persona for {student_id}: {persona}")

    # Visualize overall class performance
    class_performance = visualize_class_performance(performance_df)

if __name__ == "__main__":
    main()
