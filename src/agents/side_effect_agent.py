import os
import sys
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning, message=".*Pydantic V1 functionality isn't compatible.*")


# Add the project root to sys.path to resolve 'src' when running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from groq import Groq
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool
from src.knowledge_engine import query_knowledge_base
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def run_side_effect_agent(user_message: str, patient_context: str):
    """
    Specialist for managing GLP-1 side effects using RAG data.
    """
    # 1. Fetch the actual medical protocols from your PDFs
    clinical_evidence = query_knowledge_base(user_message)
    
    system_prompt = (
        "You are the GlycoTwin Side-Effect Concierge. Your goal is to help patients "
        "manage GLP-1 symptoms using normalcy framing and evidence-based protocols. "
        "Use the following research data to inform your answer: " + str(clinical_evidence) + "\n\n"
        "YOU MUST RESPOND IN THIS SEQUENCE WITH DOUBLE NEW LINES:\n\n"
        "**SYMPTOM ANALYSIS**\n"
        "(Acknowledge the symptom and explain if it is a common side effect of the medication.)\n\n"
        "**CLINICAL INSIGHT**\n"
        "(Explain why this is happening based on the Research Data provided.)\n\n"
        "**RELIEF STRATEGIES**\n"
        "(Give 3-4 bulleted tips like 'Small frequent meals' or 'Electrolyte hydration'.)\n\n"
        "**CLINICAL NOTE**\n"
        "Include this disclaimer: 'This is medical information from research protocols. If symptoms are severe, contact your doctor immediately.'"
    )

    completion = await run_in_threadpool(
        lambda: client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {patient_context}\nSymptom: {user_message}"}
            ],
            temperature=0.4
        )
    )
    return completion.choices[0].message.content