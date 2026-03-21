-- Run this in the Supabase SQL editor to set up the tables.

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    default_budget INTEGER DEFAULT 2000,
    preferred_currency TEXT DEFAULT 'USD',
    travel_preferences JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    destination TEXT NOT NULL,
    start_date DATE,
    duration_days INTEGER NOT NULL,
    budget_usd INTEGER NOT NULL,
    preferences TEXT,
    itinerary_json JSONB,
    itinerary_markdown TEXT,
    total_estimated_cost NUMERIC(10,2),
    status TEXT DEFAULT 'completed' CHECK (status IN ('planning', 'completed', 'error')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    tool_name TEXT,
    content TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_trip_id ON agent_logs(trip_id);
