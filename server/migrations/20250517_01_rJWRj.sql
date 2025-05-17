-- 
-- depends: 20250516_01_ChRdE
-- 1. Add a messages table, linked to users and programs, with content and from fields
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE
    SET
        NULL,
        content TEXT NOT NULL,
        "from" TEXT NOT NULL,
        -- e.g., 'student', 'professor', etc.
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Add a languages table, linked to classroom, that stores language code as primary key and language name
CREATE TABLE languages (
    code TEXT PRIMARY KEY,
    -- e.g., 'en', 'ka'
    name TEXT NOT NULL,
    classroom_id INTEGER REFERENCES classrooms(id) ON DELETE CASCADE
);

-- 3. Add an algorithm field to the summaries table (optional text)
ALTER TABLE
    summaries
ADD
    COLUMN algorithm TEXT;