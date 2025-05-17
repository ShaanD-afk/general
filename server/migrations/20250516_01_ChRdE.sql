-- depends: 
--
CREATE TABLE classrooms (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK (role IN ('student', 'professor')) NOT NULL,
    class_id INTEGER REFERENCES classrooms(id)
);

-- Now that users exist, we can link classrooms to professors (who are users)
ALTER TABLE
    classrooms
ADD
    COLUMN professor_id INTEGER REFERENCES users(id) UNIQUE;

CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    code TEXT,
    created_by INTEGER REFERENCES users(id),
    class_id INTEGER REFERENCES classrooms(id)
);

CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    language TEXT NOT NULL,
    summary TEXT NOT NULL,
    test_cases JSONB,
    audio_link TEXT
);

-- ensure one summary per language per program
CREATE UNIQUE INDEX summaries_program_language_idx ON summaries(program_id, language);

CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    program_id INTEGER REFERENCES programs(id),
    code TEXT NOT NULL,
    has_error BOOLEAN NOT NULL,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quiz_marks (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    program_id INTEGER REFERENCES programs(id),
    marks INTEGER NOT NULL CHECK (marks >= 0),
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);