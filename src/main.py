import sys
import os
import uvicorn
import json
import warnings

from fastapi import FastAPI, HTTPException
from groq import Groq
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning, message=".*Pydantic V1 functionality isn't compatible.*")

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import safety, routing, and database logic
from src.safety import check_emergency, redact_sensitive_doses
from src.db_client import PatientGraphClient 
from src.router import classify_intent
from src.knowledge_engine import query_knowledge_base

# NEW: Import all specialized agents
from src.agents.side_effect_agent import run_side_effect_agent
from src.agents.meal_agent import run_meal_agent
from src.agents.vitals_agent import run_vitals_agent

load_dotenv()

app = FastAPI(title="GlycoTwin Clinical API")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.post("/chat")
async def chat_with_glycotwin(patient_id: str, message: str):
    """
    GlycoTwin Orchestrator:
    Routes users to the Meal Specialist, Side-Effect Specialist, or Vitals Analyst.
    """
    
    # 1. HARD SAFETY CHECK (Self-harm/Emergency)
    emergency = check_emergency(message)
    if emergency:
        return emergency

    try:
        # 2. INTENT ROUTING (Triage)
        intent_json_str = await classify_intent(message)
        intent_data = json.loads(intent_json_str)
        intent_name = intent_data.get("intent")
        urgency = intent_data.get("urgency", "low")

        # --- KEYWORD OVERRIDE (Safety Net) ---
        # Ensures specific words ALWAYS trigger the right specialist
        food_keywords = ["salad", "lunch", "protein", "ate", "dinner", "breakfast", "meal"]
        symptom_keywords = ["nausea", "sick", "stomach", "dizzy", "vomit", "constipat", "pain"]
        vitals_keywords = ["weight", "lb", "kg", "pressure", "bp", "heart rate", "pulse", "bpm"]

        if any(word in message.lower() for word in food_keywords):
            intent_name = "meal_analysis"
        elif any(word in message.lower() for word in symptom_keywords):
            intent_name = "side_effect_report"
        elif any(word in message.lower() for word in vitals_keywords):
            intent_name = "vitals_log"

        # 3. BUILD DIGITAL TWIN CONTEXT
        graph_client = PatientGraphClient(patient_id)
        digital_twin = await graph_client.build_digital_twin()
        context_summary = json.dumps(digital_twin, default=str) if digital_twin.get("demographics") else "New patient: No history."

        # 4. AGENT ORCHESTRATION (The Action Layer)
        if intent_name == "meal_analysis":
            final_response = await run_meal_agent(message, context_summary)
            agent_used = "Meal Intelligence Agent"
            # LOG TO DIGITAL TWIN
            await graph_client.log_patient_event("meal", message)
            
        elif intent_name == "side_effect_report" or intent_name == "dose_question":
            final_response = await run_side_effect_agent(message, context_summary)
            agent_used = "Side-Effect Concierge"
            # LOG TO DIGITAL TWIN
            await graph_client.log_patient_event("side_effect", message)

        elif intent_name == "vitals_log":
            final_response = await run_vitals_agent(message, context_summary)
            agent_used = "Vitals Analyst"
            # LOG TO DIGITAL TWIN
            await graph_client.log_patient_event("vitals", message)
            
        else:
            # FALLBACK: Primary Brain
            brain_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are the GlycoTwin General Assistant. Provide helpful, non-prescriptive info."},
                    {"role": "user", "content": message}
                ]
            )
            final_response = brain_completion.choices[0].message.content
            agent_used = "Primary Brain"

        # 5. FINAL SAFETY SCRUB
        safe_response = redact_sensitive_doses(final_response)

        return {
            "status": "success",
            "intent_detected": intent_name,
            "handled_by": agent_used,
            "urgency_level": urgency,
            "glycotwin_response": safe_response,
            "digital_twin_updated": True
        }

    except Exception as e:
        print(f"Error in GlycoTwin Orchestrator: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)