from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from recommender.engine import RecommendationEngine

app = FastAPI()
engine = RecommendationEngine()

class QueryRequest(BaseModel):
    query: str # [cite: 169]

class AssessmentResponse(BaseModel):
    url: str # [cite: 183]
    name: str # [cite: 183]
    adaptive_support: str # [cite: 183]
    description: str # [cite: 183]
    duration: int # [cite: 183]
    remote_support: str # [cite: 183]
    test_type: List[str] # [cite: 183]

class RecommendationResponse(BaseModel):
    recommended_assessments: List[AssessmentResponse] # [cite: 174]

@app.get("/health")
def health_check():
    # Must return exact JSON [cite: 161]
    return {"status": "healthy"} 

@app.post("/recommend", response_model=RecommendationResponse)
def recommend_assessments(request: QueryRequest):
    # Retrieve recommendations
    recs = engine.recommend(request.query)
    
    # Format according to the expected API structure
    formatted_recs = []
    for r in recs:
        formatted_recs.append(AssessmentResponse(
            url=r.get("url", ""),
            name=r.get("name", ""),
            adaptive_support=r.get("adaptive_support", "No"),
            description=r.get("description", ""),
            duration=int(r.get("duration", 0)),
            remote_support=r.get("remote_support", "Yes"),
            test_type=r.get("test_type", [])
        ))
        
    return RecommendationResponse(recommended_assessments=formatted_recs)