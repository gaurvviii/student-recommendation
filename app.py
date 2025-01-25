import streamlit as st
import pandas as pd
from main import PerformanceAnalyzer
import matplotlib.pyplot as plt

st.set_page_config(page_title="Student Performance Analysis", layout="wide")

def main():
    st.title("Student Performance Analysis Dashboard")
    
    # Initialize analyzer
    analyzer = PerformanceAnalyzer()
    
    # Load data
    if not analyzer.load_data():
        st.error("Failed to load data files. Please check if the data files exist in the data/ directory.")
        return
    
    # Process submissions
    df = analyzer.analyze_submissions()
    if df.empty:
        st.error("No submission data available for analysis.")
        return
    
    # Sidebar - Student Selection
    st.sidebar.header("Student Selection")
    student_ids = df['student_id'].unique()
    selected_student = st.sidebar.selectbox("Select Student ID", student_ids)
    
    # Filter data for selected student
    student_data = df[df['student_id'] == selected_student]
    
    # Display Student Overview
    st.header("Student Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Average Accuracy",
            f"{student_data['accuracy'].mean():.1f}%",
            f"{student_data['accuracy'].mean() - df['accuracy'].mean():.1f}% vs overall"
        )
    
    with col2:
        st.metric(
            "Total Questions Attempted",
            student_data['total_questions'].sum()
        )
    
    with col3:
        st.metric(
            "Number of Quizzes Taken",
            len(student_data)
        )
    
    # Performance Trends
    st.header("Performance Analysis")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Topic Performance", "Time Trends", "Question Distribution"])
    
    with tab1:
        st.subheader("Performance by Topic")
        topic_perf = student_data.groupby('topic')['accuracy'].agg(['mean', 'count']).round(2)
        topic_perf.columns = ['Average Accuracy', 'Number of Attempts']
        st.dataframe(topic_perf)
        
        # Topic performance plot
        fig, ax = plt.subplots(figsize=(10, 6))
        topic_perf['Average Accuracy'].sort_values().plot(kind='barh', ax=ax)
        ax.set_title('Average Accuracy by Topic')
        ax.set_xlabel('Accuracy (%)')
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Performance Over Time")
        time_data = student_data.set_index('submission_date').sort_index()
        
        # Time series plot
        fig, ax = plt.subplots(figsize=(10, 6))
        time_data['accuracy'].plot(ax=ax, marker='o')
        ax.set_title('Accuracy Trend')
        ax.set_xlabel('Submission Date')
        ax.set_ylabel('Accuracy (%)')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Rolling average
        if len(time_data) > 1:
            st.line_chart(time_data['accuracy'].rolling('7D').mean())
    
    with tab3:
        st.subheader("Question Distribution")
        correct_ratio = student_data['correct_answers'] / student_data['total_questions']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        correct_ratio.hist(ax=ax, bins=20)
        ax.set_title('Distribution of Correct Answer Ratios')
        ax.set_xlabel('Correct Answer Ratio')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)
    
    # Insights
    st.header("Performance Insights")
    insights = analyzer.generate_insights()
    for insight in insights:
        st.write(insight)
    
    # Student Recommendations
    st.header("Recommendations")
    weak_topics = topic_perf[topic_perf['Average Accuracy'] < topic_perf['Average Accuracy'].mean()].index.tolist()
    
    if weak_topics:
        st.write("Focus areas for improvement:")
        for topic in weak_topics:
            st.write(f"• {topic}")
        
        st.write("\nRecommended actions:")
        st.write("1. Review fundamental concepts in the identified weak areas")
        st.write("2. Practice more questions in these topics")
        st.write("3. Consider seeking additional help for challenging topics")
    else:
        st.write("Great job! Keep maintaining consistent performance across all topics.")

if __name__ == "__main__":
    main()