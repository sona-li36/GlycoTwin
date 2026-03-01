import os
import json
import asyncio
from dotenv import load_dotenv
class PatientGraphClient:
    def __init__(self, patient_id):
        self.patient_id = str(patient_id).lower()
        self.file_path = "demo_memory.json"
        # Create a fresh memory file if it doesn't exist
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"meals_log": [], "side_effects_log": [], "vitals": []}, f)

    def load_data(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f)

    async def log_patient_event(self, event_type: str, message: str):
        """Saves data to a local file so the demo NEVER fails."""
        data = self.load_data()
        if event_type == "meal":
            data["meals_log"].append({"meal_description": message})
        elif event_type == "side_effect":
            data["side_effects_log"].append({"symptom": message})
        elif event_type == "vitals":
            data["vitals"].append({"metrics": message})
        self.save_data(data)
        return True

    async def build_digital_twin(self):
        """Feeds the saved data directly to the Report Agent."""
        data = self.load_data()
        return {
            "meals_log": data["meals_log"],
            "side_effects_log": data["side_effects_log"],
            "vitals": data["vitals"],
            "demographics": {"status": "Active", "name": "Demo Patient"}
        }