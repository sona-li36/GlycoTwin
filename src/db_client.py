import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fetch_glycotwin_context(patient_id):
    """Assembles the Digital Twin data for the AI agents."""
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    # 8 Parallel Queries for real-time context building
    queries = [
        conn.fetchrow("SELECT * FROM patients WHERE id = $1", patient_id),
        conn.fetchrow("SELECT * FROM glp1_prescriptions WHERE patient_id = $1", patient_id),
        conn.fetch("SELECT * FROM biomarker_values WHERE patient_id = $1 ORDER BY created_at DESC LIMIT 10", patient_id),
        conn.fetch("SELECT * FROM side_effect_logs WHERE patient_id = $1 ORDER BY logged_at DESC LIMIT 5", patient_id),
        conn.fetch("SELECT * FROM weight_trajectory WHERE patient_id = $1 LIMIT 5", patient_id),
        conn.fetch("SELECT * FROM action_plans WHERE patient_id = $1 ORDER BY generated_at DESC LIMIT 1", patient_id),
        conn.fetchrow("SELECT * FROM questionnaires WHERE patient_id = $1", patient_id),
        conn.fetch("SELECT * FROM wearable_daily_summary WHERE patient_id = $1 LIMIT 1", patient_id)
    ]
    
    results = await asyncio.gather(*queries)
    await conn.close()
    
    return {
        "profile": results[0],
        "medication": results[1],
        "labs": results[2],
        "side_effects": results[3]
    }