-- Enable UUID support
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. GlycoTwin Patient Core
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dob DATE,
    sex_at_birth VARCHAR(10) CHECK (sex_at_birth IN ('M', 'F', 'OTHER')),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. GLP-1 Precision Dosing History
CREATE TABLE glp1_prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    drug VARCHAR(50) NOT NULL,
    current_dose_mg DECIMAL(5,2) NOT NULL,
    titration_schedule JSONB, 
    start_date DATE NOT NULL
);

-- 3. Side-Effect & Tolerance Logs
CREATE TABLE side_effect_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    symptom_type VARCHAR(50) NOT NULL,
    severity_0_10 INT CHECK (severity_0_10 BETWEEN 0 AND 10),
    logged_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Metabolic & Nutrient Biomarkers
CREATE TABLE biomarker_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    biomarker_code VARCHAR(50) NOT NULL,
    value DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20),
    status VARCHAR(20)
);

-- 5. Add a Test Patient (Note: We use a specific UUID to match your testing)
INSERT INTO patients (id, dob, sex_at_birth, weight_kg) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', '1990-01-01', 'F', 85.0);

-- 6. Meals Log
CREATE TABLE meals_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    meal_time TIMESTAMPTZ DEFAULT NOW(),
    meal_description TEXT,
    calories DECIMAL(6,2),
    protein_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fat_g DECIMAL(6,2)
);

-- 7. Vitals
CREATE TABLE vitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    weight_kg DECIMAL(5,2),
    systolic_bp INT,
    diastolic_bp INT,
    heart_rate INT,
    glucose_mg_dl DECIMAL(6,2),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Lifestyle
CREATE TABLE lifestyle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    sleep_hours DECIMAL(4,2),
    exercise_minutes INT,
    stress_level INT CHECK (stress_level BETWEEN 0 AND 10),
    alcohol BOOLEAN,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Goals
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    target_weight_kg DECIMAL(5,2),
    fertility_goal BOOLEAN,
    energy_goal BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);