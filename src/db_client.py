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

    async def fetch_history(self, table_name, limit=5):
        """Helper to fetch a list of recent records for trend analysis"""
        async with AsyncSessionLocal() as session:
            try:
                # We fetch MULTIPLE records (limit 5) so the Report Agent has data to summarize
                result = await session.execute(
                    text(f"SELECT * FROM {table_name} WHERE patient_id = :p_id ORDER BY created_at DESC LIMIT :limit"),
                    {"p_id": self.patient_id, "limit": limit}
                )
                return result.mappings().all()
            except Exception as e:
                print(f"Error fetching history from {table_name}: {e}")
                return []

    async def get_patient_details(self):
        """Specific fetch for the core demographics table"""
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    text("SELECT * FROM patients WHERE id = :p_id"),
                    {"p_id": self.patient_id}
                )
                return result.mappings().first()
            except Exception as e:
                print(f"Error fetching patient details: {e}")
                return None

    async def build_digital_twin(self):
        """
        Module 1: Digital Twin (PatientGraph)
        Constructs the full context for specialized agents.
        """
        tasks = [
            self.get_patient_details(),                               
            self.fetch_history("glp1_prescriptions", limit=1),    
            self.fetch_history("biomarker_values", limit=3),        
            self.fetch_history("side_effect_logs", limit=5),      
            self.fetch_history("meals_log", limit=5),                    
            self.fetch_history("vitals", limit=5),                      
            self.fetch_history("lifestyle", limit=1),                
            self.fetch_history("goals", limit=1)                         
        ]

        results = await asyncio.gather(*tasks)

        # Structure the data for the specialist agents
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
        """Logs patient events with forced timestamps to ensure they appear in history."""
        async with AsyncSessionLocal() as session:
            try:
                # We use CURRENT_TIMESTAMP to ensure the DB sees the time immediately
                if event_type == "meal":
                    query = text("INSERT INTO meals_log (patient_id, meal_description, created_at) VALUES (:p_id, :msg, CURRENT_TIMESTAMP)")
                elif event_type == "side_effect":
                    query = text("INSERT INTO side_effect_logs (patient_id, symptom, created_at) VALUES (:p_id, :msg, CURRENT_TIMESTAMP)")
                elif event_type == "vitals":
                    query = text("INSERT INTO vitals (patient_id, metrics, created_at) VALUES (:p_id, :msg, CURRENT_TIMESTAMP)")
                else:
                    return False
                    
                await session.execute(query, {"p_id": self.patient_id.lower(), "msg": message})
                await session.commit()
                print(f"✅ DB SUCCESS: Logged {event_type}") # This will show in your server logs
                return True
            except Exception as e:
                print(f"❌ DB ERROR: {e}")
                await session.rollback()
                return False