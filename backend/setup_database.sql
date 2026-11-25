CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS planner_users(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,email text UNIQUE NOT NULL,password_hash text NOT NULL,role text NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')));
CREATE TABLE IF NOT EXISTS planner_shortlist(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,user_id bigint NOT NULL REFERENCES planner_users(id) ON DELETE CASCADE,name text NOT NULL,latitude double precision NOT NULL CHECK(latitude BETWEEN -90 AND 90),longitude double precision NOT NULL CHECK(longitude BETWEEN -180 AND 180));
CREATE TABLE IF NOT EXISTS planner_preferences(user_id bigint PRIMARY KEY REFERENCES planner_users(id) ON DELETE CASCADE,charger_type text NOT NULL,coverage_gap double precision NOT NULL,commercial_facilities double precision NOT NULL,road_proximity double precision NOT NULL);
CREATE TABLE IF NOT EXISTS planner_stations(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,name text NOT NULL,latitude double precision NOT NULL CHECK(latitude BETWEEN -90 AND 90),longitude double precision NOT NULL CHECK(longitude BETWEEN -180 AND 180));
ALTER TABLE planner_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE planner_shortlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE planner_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE planner_stations ENABLE ROW LEVEL SECURITY;
