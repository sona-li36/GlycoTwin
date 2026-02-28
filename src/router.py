import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def classify_intent(user_message: str):
    try:
        completion = client.chat.completions.create(
            model="llama-3.2-3b-preview", 
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are the GlycoTwin Triage Nurse. Categorize input into ONE intent:\n"
                        "1. 'meal_analysis': If message mentions food (salad, lunch, chicken, eggs, calories, protein).\n"
                        
                        "2. 'side_effect_report': If message mentions symptoms (nausea, sick, dizzy, stomach).\n"
                        "3. 'vitals_log': Mention of weight, BP, blood pressure, heart rate, or numbers.\n"
                        "4. 'dose_question': If message mentions shot, schedule, titration, or mg.\n"
                        "5. 'general_health': Everything else.\n\n"
                        "EXAMPLES:\n"
                        "Input: 'I had a salad' -> {'intent': 'meal_analysis', 'urgency': 'low'}\n"
                        "Input: 'I feel sick' -> {'intent': 'side_effect_report', 'urgency': 'medium'}\n"
                        "Output ONLY JSON."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        return json.dumps({"intent": "general_health", "urgency": "low"})