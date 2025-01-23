# app/main.py

from fastapi import FastAPI, HTTPException
from .services.analyzer import QuizAnalyzer
from .services.recommender import QuizRecommender
from .schemas.quiz import QuizData, HistoricalData, Analysis

app = FastAPI()

@app.post("/analyze", response_model=Analysis)
async def analyze_quiz(
    current_quiz: QuizData,
    historical_data: HistoricalData
):
    try:
        analyzer = QuizAnalyzer(
            current_quiz.dict(),
            historical_data.dict()['quizzes']
        )
        analysis = analyzer.analyze_performance()
        
        recommender = QuizRecommender(analysis)
        recommendations = recommender.generate_recommendations()
        
        return {
            "analysis": analysis,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
