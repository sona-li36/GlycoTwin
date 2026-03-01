import os
from groq import Groq
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def run_vitals_agent(user_message: str, patient_context: str):
    """
    Specialist for analyzing weight, BP, and heart rate trends.
    """
    system_prompt = (
        "You are the GlycoTwin Vitals Analyst. Your job is to interpret biometrics. "
        "Use the following sequence with double new lines:\n\n"
        "**VITALS ASSESSMENT**\n"
        "(Analyze the numbers provided. Compare them to the patient's historical context if available.)\n\n"
        "**TREND ANALYSIS**\n"
        "(Explain if the numbers are within a healthy range for someone on GLP-1 therapy.)\n\n"
        "**GLYCOTWIN GUIDANCE**\n"
        "(Suggest a next step, like 'Continue monitoring' or 'Reduce salt intake'.)\n\n"
        "**CLINICAL NOTE**\n"
        "Include: 'This is a data analysis, not a diagnosis. Contact your doctor for high BP readings (e.g., >140/90).'"
    )

    completion = await run_in_threadpool(
        lambda: client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {patient_context}\nNew Vitals: {user_message}"}
            ],
            temperature=0.3
        )
    )
    return completion.choices[0].message.content
    # update test
    