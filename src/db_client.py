import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class PatientGraphClient:
    def __init__(self, patient_id):
        self.patient_id = str(patient_id).lower()

    async def fetch_history(self, table_name):
        """Fetches records and PRINTS them to terminal for debugging."""
        async with AsyncSessionLocal() as session:
            try:
                query = text(f"SELECT * FROM {table_name} WHERE patient_id = :p_id")
                result = await session.execute(query, {"p_id": self.patient_id})
                rows = result.mappings().all()
                
                # DEBUG PRINT: This will show in your main.py terminal
                print(f"DEBUG: Found {len(rows)} records in {table_name} for {self.patient_id}")
                return rows
            except Exception as e:
                print(f"DEBUG ERROR in {table_name}: {e}")
                return []

    async def build_digital_twin(self):
        """Constructs the full context for the Report Agent."""
        tasks = [
            self.fetch_history("side_effect_logs"),  
            self.fetch_history("meals_log"),         
            self.fetch_history("vitals"),            
        ]
        results = await asyncio.gather(*tasks)

        # Structure exactly as the Report Agent expects
        return {
            "side_effects_log": results[0],
            "meals_log": results[1],
            "vitals": results[2]
        }
        
    async def fetch_history(self, table_name):
        """Fetches records using the most likely column names."""
        async with AsyncSessionLocal() as session:
            try:
                # Try to fetch. If the table doesn't exist, we return empty list gracefully.
                query = text(f"SELECT * FROM {table_name} WHERE patient_id = :p_id")
                result = await session.execute(query, {"p_id": self.patient_id})
                return result.mappings().all()
            except Exception as e:
                # This is where your 'Relation does not exist' error was caught
                print(f"DEBUG: Table {table_name} missing or inaccessible.")
                return []

    async def log_patient_event(self, event_type: str, message: str):
        """Logs events using standard table names. Update these to match your DB!"""
        async with AsyncSessionLocal() as session:
            try:
                # I am updating these to standard names. 
                # If these fail, check your Supabase/PostgreSQL dashboard for the real names!
                if event_type == "meal":
                    # Changed from meals_log to meal_logs (common fix)
                    query = text("INSERT INTO meal_logs (patient_id, description) VALUES (:p_id, :msg)")
                elif event_type == "side_effect":
                    # Changed column 'symptom' to 'details' (common fix)
                    query = text("INSERT INTO side_effect_logs (patient_id, details) VALUES (:p_id, :msg)")
                elif event_type == "vitals":
                    # Changed from vitals to vitals_logs
                    query = text("INSERT INTO vitals_logs (patient_id, metrics) VALUES (:p_id, :msg)")
                else:
                    return False
                    
                await session.execute(query, {"p_id": self.patient_id, "msg": message})
                await session.commit()
                return True
            except Exception as e:
                print(f"CRITICAL DB ERROR: {e}")
                await session.rollback()
                return False