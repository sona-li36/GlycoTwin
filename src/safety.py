import re

# Critical keywords for immediate bypass
EMERGENCY_KEYWORDS = ["chest pain", "shortness of breath", "can't breathe", "suicidal"]

# Words that signal the AI is giving a direct medical order
DIRECTIVE_WORDS = [
    "i recommend", "you should", "you must", "take", 
    "increase to", "decrease to", "change your dose", "prescribe",
    "suggest taking", "start taking"
]

def check_emergency(text: str):
    """Zero-latency check for critical symptoms."""
    if any(k in text.lower() for k in EMERGENCY_KEYWORDS):
        return {
            "intent": "emergency", 
            "response": "⚠️ GlycoTwin Alert: CALL EMERGENCY SERVICES (112) IMMEDIATELY. Your symptoms require urgent medical review."
        }
    return None

def redact_sensitive_doses(text: str):
    """
    Blocks specific doses ONLY if they appear alongside directive language.
    This allows educational schedules from your PDFs to pass through.
    """
    text_lower = text.lower()
    
    # Check if the AI is using "Directive" or "Prescriptive" language
    is_prescriptive = any(word in text_lower for word in DIRECTIVE_WORDS)
    
    if is_prescriptive:
        # If directive, redact all dose numbers (e.g., '0.25mg' -> '[REDACTED DOSE]')
        # This protects you from the AI giving unauthorized medical advice
        return re.sub(r'\d+(\.\d+)?\s?mg', '[REDACTED DOSE]', text)
    
    # If the text is purely informational (like a titration table), keep the doses
    return text