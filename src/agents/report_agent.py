import os
from groq import Groq
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def run_report_agent(patient_context: str):
    """
    Summarizes the Digital Twin history into a clinical SOAP note.
    """
    system_prompt = (
        "You are the GlycoTwin Clinical Reporter. Your job is to summarize patient logs "
        "for a healthcare provider. Use a professional, clinical tone.\n\n"
        "USE THIS SEQUENCE:\n\n"
        "**CLINICAL SUMMARY REPORT**\n\n"
        "**SUBJECTIVE (Patient Reports)**\n"
        "(Summarize logged symptoms and meal quality.)\n\n"
        "**OBJECTIVE (Biometric Data)**\n"
        "(Summarize weight and blood pressure readings.)\n\n"
        "**ASSESSMENT (GlycoTwin Analysis)**\n"
        "(Identify trends, e.g., 'BP is rising while protein intake is low'.)\n\n"
        "**RECOMMENDED ACTION PLAN**\n"
        "(List 2-3 clinical priorities for the next visit.)"
    )

    completion = await run_in_threadpool(
        lambda: client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Full Digital Twin History: {patient_context}"}
            ],
            temperature=0.2
        )
    )
    return completion.choices[0].message.content