import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/chat"
# Use the UUID that worked for your database
PATIENT_ID = "a1111111-1111-1111-1111-111111111111" 

def run_step(step_name, message, is_report=False):
    print(f"\n--- STEP: {step_name} ---")
    print(f"User says: '{message}'")
    
    if is_report:
        print("⏳ Analyzing history and generating clinical report... (please wait)")

    params = {"patient_id": PATIENT_ID, "message": message}
    
    try:
        # Increased timeout to 30 seconds for the Report Agent
        response = requests.post(BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Handled by: {data['handled_by']}")
            print("\nGlycoTwin Response:")
            # Use splitlines to ensure clean printing of paragraphs
            print(data['glycotwin_response'])
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Error: The request timed out. The Report Agent took too long to respond.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def main():
    print("🚀 STARTING GLYCOTWIN MULTI-AGENT DEMO")
    
    # 1. Meal Check
    run_step("Meal Check", "I had a small salad for lunch with no protein.")
    time.sleep(1)
    
    # 2. Symptom Log
    run_step("Symptom Log", "I'm feeling really dizzy and lightheaded today.")
    time.sleep(1)
    
    # 3. Vitals Check
    run_step("Vitals Check", "My blood pressure is 142/92.")
    time.sleep(2) # Give the DB a moment to settle
    
    # 4. The Final Clinical Summary
    print("\n" + "="*60)
    print("📋 GENERATING FINAL DOCTOR'S SUMMARY REPORT")
    print("="*60)
    # Pass 'is_report=True' to show the loading message
    run_step("Final Report", "Please summarize my history for my doctor's visit.", is_report=True)
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()