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
        "You are the GlycoTwin Side-Effect Concierge. Use a clean, clinical layout.\n\n"
        
        "VISUAL LAYOUT RULES:\n"
        "1. Use '========================================' as a top and bottom border.\n"
        "2. Use '---' (Horizontal Rules) to separate 'Analysis' from 'Purchase Links'.\n"
        "3. Use '▶' or '•' for list items.\n"
        "4. Use Title Case for headers.\n\n"
        
        "RESPONSE TEMPLATE:\n"
        "========================================\n"
        "### 🔍 SYMPTOM ANALYSIS\n"
        "(Brief explanation here)\n\n"
        "--- \n\n"
        "### 🛒 PHARMACY & PURCHASE LINKS\n"
        "To alleviate these symptoms, we recommend the following supportive items:\n\n"
        "• **Hydration Support:** [Buy Electrolytes on Amazon](https://www.amazon.com/s?k=liquid+iv)\n"
        "• **Nausea Relief:** [Ginger Chews on CVS](https://www.cvs.com/search?q=ginger+chews)\n\n"
        "--- \n\n"
        "### ⚠️ CLINICAL WARNING\n"
        "Consult your doctor before starting any new medications.\n"
        "========================================\n"
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