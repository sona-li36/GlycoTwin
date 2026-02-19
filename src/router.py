import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client using your API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def classify_intent(user_message: str):
    """
    Uses the Llama 3.3 70B model to classify user messages into specific 
    clinical intents for the GlycoTwin platform.
    """
    try:
        # We use the 70B model for its superior clinical reasoning capabilities
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are the GlycoTwin Intent Classifier. Categorize the user's input into exactly one of these categories: "
                        "[side_effect_report, meal_analysis, dose_question, explain_report, lifestyle_coaching, "
                        "generate_action_plan, general_health]. "
                        "Output ONLY a valid JSON object with the keys 'intent' and 'urgency'."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            # Ensures the model output is strictly JSON
            response_format={"type": "json_object"}
        )

        # Extract and return the JSON string from the response
        return completion.choices[0].message.content

    except Exception as e:
        # Basic error handling for API connection issues
        return json.dumps({
            "intent": "general_health",
            "urgency": "low",
            "error": str(e)
        })