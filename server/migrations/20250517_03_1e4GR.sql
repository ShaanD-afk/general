-- 
-- depends: 20250517_02_K6kNo
CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    class_id INTEGER REFERENCES classrooms(id) ON DELETE CASCADE,
    questions JSONB NOT NULL,
    marks INTEGER
);

