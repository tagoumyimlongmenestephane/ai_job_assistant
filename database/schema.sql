
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    base_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table 2: Job listings
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,

    source_id INTEGER REFERENCES sources(id),

    external_reference VARCHAR(150) NOT NULL,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),

    description TEXT,
    city VARCHAR(150),
    postal_code VARCHAR(20),

    salary_min NUMERIC(10,2),
    salary_max NUMERIC(10,2),
    pay_unit VARCHAR(50),

    contract_type VARCHAR(50),
    distance_km NUMERIC(8,2),

    published_at TIMESTAMP,
    application_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (source_id, external_reference)
);


-- Table 3: Job listing analyses
CREATE TABLE job_analyses (
    id SERIAL PRIMARY KEY,

    job_id INTEGER NOT NULL REFERENCES jobs(id)
        ON DELETE CASCADE,

    matching_score NUMERIC(5,2),
    matching_coverage NUMERIC(5,2),

    required_skills JSONB,
    matched_skills JSONB,
    missing_skills JSONB,

    ai_relevance VARCHAR(30),
    recommendation VARCHAR(50),

    ai_analysis JSONB,
    analysis_model VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table 4: Applications
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,

    job_id INTEGER NOT NULL UNIQUE REFERENCES jobs(id)
        ON DELETE CASCADE,

    status VARCHAR(50) DEFAULT 'TO_REVIEW',

    applied_at TIMESTAMP,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Indexes to speed up searches
CREATE INDEX idx_jobs_city ON jobs(city);
CREATE INDEX idx_jobs_published ON jobs(published_at);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_analyses_score ON job_analyses(matching_score);
