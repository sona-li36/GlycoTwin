import uvicorn
import json
from fastapi import FastAPI, HTTPException
from src.safety import check_emergency, redact_sensitive_doses
from src.db_client import fetch_glycotwin_context
from src.router import classify_intent

app = FastAPI(title="GlycoTwin Clinical API")

@app.post("/chat")
async def chat_with_glycotwin(patient_id: str, message: str):
    # 1. Hard Safety Check (Zero-Latency)
    # Runs before any AI logic to ensure immediate emergency response
    emergency = check_emergency(message)
    if emergency:
        return emergency

    try:
        # 2. Build PatientGraph (Digital Twin)
        # Fetches labs, dose history, and vitals in parallel
        context = await fetch_glycotwin_context(patient_id)
        if not context["profile"]:
            raise HTTPException(status_code=404, detail="Patient not found")

        # 3. Intent Classification (Llama 3.3 70B via Groq)
        # Decides if this is a side effect, meal, or lab question
        intent_json_str = await classify_intent(message)
        intent_data = json.loads(intent_json_str)

        # 4. Routing Logic
        # Based on the intent, you would eventually call a specific agent
        intent_name = intent_data.get("intent")
        
        return {
            "status": "success",
            "project": "GlycoTwin",
            "intent": intent_name,
            "urgency": intent_data.get("urgency", "low"),
            "data_context_loaded": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)