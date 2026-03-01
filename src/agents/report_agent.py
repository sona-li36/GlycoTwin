import os
from groq import Groq
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def run_report_agent(patient_context: str):
    """
    Summarizes the Digital Twin history into a clinical SOAP note.
    Uses Markdown formatting for a clean, professional appearance.
    """
    
    system_prompt = (
        "You are the GlycoTwin Clinical Reporter. Your job is to summarize patient logs "
        "for a healthcare provider using a professional, structured medical format.\n\n"
        
        "FORMATTING RULES:\n"
        "1. Use '---' (Horizontal Rules) to separate the three main sections.\n"
        "2. Use '###' for Section Headers.\n"
        "3. Use bullet points for specific data points to ensure scannability.\n"
        "4. Use Bold text for labels (e.g., **BP:**).\n\n"
        
        "CRITICAL INSTRUCTION:\n"
        "Summarize ALL available data in the context. If you see 'meals_log', 'side_effects_log', "
        "or 'vitals', you MUST include them. Do not say 'No data available' if data exists.\n\n"
        
        "STRUCTURE YOUR RESPONSE AS FOLLOWS:\n\n"
        "# CLINICAL SUMMARY REPORT\n"
        "--- \n"
        "### **1. SUBJECTIVE: PATIENT REPORTS**\n"
        "* **Nutrition History:** (Summarize items from meals_log)\n"
        "* **Symptoms/Side Effects:** (Summarize items from side_effects_log)\n\n"
        
        "### **2. OBJECTIVE: BIOMETRIC DATA**\n"
        "* **Vitals & Metrics:** (List BP, weight, and heart rate from the vitals section)\n"
        "--- \n\n"
        
        "### **3. CLINICAL ASSESSMENT & PLAN**\n"
        "**Observation:** (Identify trends, e.g., 'Elevated BP following low protein intake')\n\n"
        "**Recommended Action Items:**\n"
        "1. (Priority item 1)\n"
        "2. (Priority item 2)\n"
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