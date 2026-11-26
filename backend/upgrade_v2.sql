BEGIN;
ALTER TABLE planner_users ADD COLUMN IF NOT EXISTS full_name text NOT NULL DEFAULT '';
ALTER TABLE planner_users ADD COLUMN IF NOT EXISTS organization text NOT NULL DEFAULT '';
ALTER TABLE planner_users ADD COLUMN IF NOT EXISTS user_type text NOT NULL DEFAULT 'Individual User';
COMMIT;
