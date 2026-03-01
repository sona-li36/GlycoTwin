import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

class PatientGraphClient:
    def __init__(self, patient_id):
        self.patient_id = str(patient_id).lower()
        self.file_path = "demo_memory.json"
        # Initialize the file as a dictionary if it doesn't exist
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)

    def load_data(self):
        """Loads the entire DB but returns ONLY the data for THIS specific patient."""
        try:
            with open(self.file_path, "r") as f:
                full_db = json.load(f)
                # If the patient doesn't exist yet, return a blank template
                return full_db.get(self.patient_id, {
                    "meals_log": [], 
                    "side_effects_log": [], 
                    "vitals": []
                })
        except (json.JSONDecodeError, FileNotFoundError):
            return {"meals_log": [], "side_effects_log": [], "vitals": []}

    def save_data(self, patient_data):
        """Updates ONLY this patient's record within the full database file."""
        full_db = {}
        # 1. Read the existing full database
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    full_db = json.load(f)
            except json.JSONDecodeError:
                full_db = {}

        # 2. Update just this patient's record
        full_db[self.patient_id] = patient_data

        # 3. Save the entire updated database back to the file
        with open(self.file_path, "w") as f:
            json.dump(full_db, f, indent=4)

    async def log_patient_event(self, event_type: str, message: str):
        """Saves data to a local file indexed by patient_id."""
        # Load THIS patient's specific data
        patient_data = self.load_data()
        
        if event_type == "meal":
            patient_data["meals_log"].append({"meal_description": message})
        elif event_type == "side_effect":
            patient_data["side_effects_log"].append({"symptom": message})
        elif event_type == "vitals":
            patient_data["vitals"].append({"metrics": message})
        
        # Save updated patient data back into the full DB
        self.save_data(patient_data)
        return True

    async def build_digital_twin(self):
        """Constructs the history context for the Report Agent for THIS patient."""
        patient_data = self.load_data()
        return {
            "meals_log": patient_data["meals_log"],
            "side_effects_log": patient_data["side_effects_log"],
            "vitals": patient_data["vitals"],
            "demographics": {"status": "Active", "id": self.patient_id}
        }