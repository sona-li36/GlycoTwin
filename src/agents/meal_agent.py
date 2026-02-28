import os
from groq import Groq
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool

load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def run_meal_agent(user_message: str, patient_context: str):
    """
    Specialist for protein tracking and meal analysis.
    Uses run_in_threadpool to prevent blocking the FastAPI event loop.
    """
    
    system_prompt = (
        "You are the GlycoTwin Meal Intelligence Specialist. "
        "Your goal is to ensure GLP-1 patients maintain muscle mass through protein-first eating. "
        "You MUST respond in the following sequence with a clear empty line between sections:\n\n"
        
        "**MEAL ANALYSIS**\n"
        "(Analyze the user's meal. Be direct: tell them if it lacks protein or fiber.)\n\n"
        
        "**WHY PROTEIN MATTERS**\n"
        "(Explain the risk of muscle loss and 'Ozempic Face' due to rapid weight loss.)\n\n"
        
        "**GLYCOTWIN RECOMMENDATIONS**\n"
        "(Suggest 2-3 specific, high-protein additions like Greek yogurt or chicken.)\n\n"
        
        "**CLINICAL NOTE**\n"
        "Include this disclaimer: 'This is nutritional guidance based on clinical protocols. Consult your provider for medical changes.'"
    )

    # We use run_in_threadpool because the Groq SDK is synchronous.
    # This prevents the server from freezing for other users.
    completion = await run_in_threadpool(
        lambda: client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Patient Context: {patient_context}\nUser Message: {user_message}"}
            ],
            temperature=0.5 # Lower temperature for more consistent formatting
        )
    )
    
    return completion.choices[0].message.content