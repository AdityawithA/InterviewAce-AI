
-- =====================================================
-- InterviewAce AI Database
-- =====================================================



-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL
    
);

-- =====================================================
-- INTERVIEWS TABLE
-- =====================================================

CREATE TABLE interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role ENUM(
        'HR Interview',
        'Frontend Developer',
        'Backend Developer',
        'Full Stack Developer',
        'Data Analyst',
        'Machine Learning Engineer'
    ) NOT NULL,
    difficulty ENUM(
        'Beginner',
        'Intermediate',
        'Advanced'
    ) NOT NULL,
    total_questions INT NOT NULL,
    score INT DEFAULT 0,
    status ENUM(
        'In Progress',
        'Completed'
    ) DEFAULT 'In Progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- =====================================================
-- QUESTIONS TABLE
-- =====================================================

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_text TEXT NOT NULL,
    answer_text LONGTEXT,
    ai_feedback LONGTEXT,
    question_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (interview_id)
    REFERENCES interviews(id)
    ON DELETE CASCADE
);

-- =====================================================
-- REPORTS TABLE
-- =====================================================

CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL UNIQUE,
    overall_score INT,
    strengths LONGTEXT,
    weaknesses LONGTEXT,
    suggestions LONGTEXT,
    report_summary LONGTEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (interview_id)
    REFERENCES interviews(id)
    ON DELETE CASCADE
);

-- =====================================================
-- RESUMES TABLE
-- =====================================================

CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_filename VARCHAR(255),
    extracted_skills LONGTEXT,
    extracted_education LONGTEXT,
    extracted_experience LONGTEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- =====================================================
-- USER STATISTICS TABLE
-- =====================================================

CREATE TABLE user_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    total_interviews INT DEFAULT 0,
    highest_score INT DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0.00,
    updated_at TIMESTAMP NULL,
    

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_users_email
ON users(email);

CREATE INDEX idx_interviews_user
ON interviews(user_id);

CREATE INDEX idx_questions_interview
ON questions(interview_id);

CREATE INDEX idx_reports_interview
ON reports(interview_id);

CREATE INDEX idx_resumes_user
ON resumes(user_id);

-- =====================================================
-- TRIGGER
-- =====================================================

DELIMITER $$

CREATE TRIGGER create_user_stats
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO user_statistics(user_id)
    VALUES (NEW.id);
END$$

DELIMITER ;

-- =====================================================
-- SAMPLE USER
-- =====================================================

INSERT INTO users (
    full_name,
    email,
    password
)
VALUES (
    'Test User',
    'test@example.com',
    'password123'
);

-- =====================================================
-- VERIFY TABLES
-- =====================================================

SHOW TABLES;

