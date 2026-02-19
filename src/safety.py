import re

# Critical keywords for immediate bypass
EMERGENCY_KEYWORDS = ["chest pain", "shortness of breath", "can't breathe", "suicidal"]

def check_emergency(text: str):
    """Zero-latency check for critical symptoms."""
    if any(k in text.lower() for k in EMERGENCY_KEYWORDS):
        return {
            "intent": "emergency", 
            "response": "⚠️ GlycoTwin Alert: CALL EMERGENCY SERVICES (112) IMMEDIATELY. Your symptoms require urgent medical review."
        }
    return None

def redact_sensitive_doses(text: str):
    """Prevents the AI from recommending specific dosage numbers."""
    # Replaces '1.5mg' or '0.25 mg' with a placeholder
    return re.sub(r'\d+(\.\d+)?\s?mg', '[REDACTED DOSE]', text)