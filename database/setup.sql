-- 1. GlycoTwin Patient Core
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dob DATE NOT NULL,
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
    titration_schedule JSONB, -- Stores the 0.25 -> 0.5 escalation logic
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
    biomarker_code VARCHAR(50) NOT NULL, -- e.g., 'A1C', 'FERRITIN'
    value DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20),
    status VARCHAR(20) -- OPTIMAL, HIGH, LOW
);