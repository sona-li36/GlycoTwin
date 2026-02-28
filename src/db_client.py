import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Ensure your DATABASE_URL uses the async driver (postgresql+asyncpg://)
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class PatientGraphClient:
    def __init__(self, patient_id):
        self.patient_id = patient_id

    async def fetch_data(self, query_name, table_name):
        """Helper to run a specific query for the Digital Twin"""
        async with AsyncSessionLocal() as session:
            try:
                # Matches your UUID schema
                result = await session.execute(
                    text(f"SELECT * FROM {table_name} WHERE patient_id = :p_id ORDER BY created_at DESC LIMIT 1"),
                    {"p_id": self.patient_id}
                )
                return result.mappings().first()
            except Exception as e:
                print(f"Error fetching {query_name}: {e}")
                return None

    async def get_patient_details(self):
        """Specific fetch for the core demographics table"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("SELECT * FROM patients WHERE id = :p_id"),
                {"p_id": self.patient_id}
            )
            return result.mappings().first()

    async def build_digital_twin(self):
        """
        Module 1: Digital Twin (PatientGraph)
        Performs 8 parallel DB queries at chat start .
        """
        # Execute all 8 queries in parallel to minimize latency 
        tasks = [
            self.get_patient_details(),                               # 1. Demographics
            self.fetch_data("glp1_history", "glp1_prescriptions"),    # 2. GLP-1 History
            self.fetch_data("biomarkers", "biomarker_values"),        # 3. Biomarkers
            self.fetch_data("side_effects", "side_effect_logs"),      # 4. Side Effects
            self.fetch_data("meals", "meals_log"),                    # 5. Meals
            self.fetch_data("vitals", "vitals"),                      # 6. Vitals
            self.fetch_data("lifestyle", "lifestyle"),                # 7. Lifestyle
            self.fetch_data("goals", "goals")                         # 8. Goals
        ]

        results = await asyncio.gather(*tasks)

        # Structure the data for the specialist agents [cite: 19-20]
        patient_graph = {
            "demographics": results[0],
            "glp1_history": results[1],
            "biomarkers": results[2],
            "side_effects_log": results[3],
            "meals_log": results[4],
            "vitals": results[5],
            "lifestyle": results[6],
            "goals": results[7]
        }

        return patient_graph
        
    async def log_patient_event(self, event_type: str, message: str):
        """Logs patient events (e.g. meals, side effects, vitals) to the database."""
        async with AsyncSessionLocal() as session:
            try:
                if event_type == "meal":
                    query = text("INSERT INTO meals_log (patient_id, meal_description) VALUES (:p_id, :msg)")
                elif event_type == "side_effect":
                    query = text("INSERT INTO side_effect_logs (patient_id, symptom) VALUES (:p_id, :msg)")
                elif event_type == "vitals":
                    query = text("INSERT INTO vitals (patient_id, metrics) VALUES (:p_id, :msg)")
                else:
                    print(f"Unknown event type: {event_type}")
                    return False
                    
                await session.execute(query, {"p_id": self.patient_id, "msg": message})
                await session.commit()
                return True
            except Exception as e:
                print(f"Error logging {event_type} event: {e}")
                await session.rollback()
                return False