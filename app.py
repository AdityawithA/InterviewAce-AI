# =====================================================
# InterviewAce AI
# app.py - Part 1
# =====================================================
import os
import json
from functools import wraps
from datetime import datetime

import mysql.connector
import google.generativeai as genai

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from config import Config


# =====================================================
# FLASK APP INITIALIZATION
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

Config.init_app(app)


# =====================================================
# GEMINI CONFIGURATION
# =====================================================

genai.configure(
    api_key=app.config["GEMINI_API_KEY"]
)

gemini_model = genai.GenerativeModel(
    app.config["GEMINI_MODEL"]
)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    """
    Create MySQL database connection
    """

    try:

        connection = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            port=app.config["MYSQL_PORT"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DATABASE"]
        )

        return connection

    except mysql.connector.Error as err:

        print(f"Database Error: {err}")

        return None


# =====================================================
# LOGIN REQUIRED DECORATOR
# =====================================================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return wrapper


# =====================================================
# FILE VALIDATION
# =====================================================

def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return (
        extension
        in app.config["ALLOWED_EXTENSIONS"]
    )


# =====================================================
# GET CURRENT USER
# =====================================================

def get_current_user():

    if "user_id" not in session:
        return None

    connection = get_db_connection()

    if not connection:
        return None

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


# =====================================================
# GEMINI QUESTION GENERATOR
# =====================================================

def generate_interview_questions(
    role,
    difficulty,
    total_questions
):
    """
    Generate interview questions using Gemini
    """

    prompt = f"""
    Generate {total_questions}
    interview questions.

    Role:
    {role}

    Difficulty:
    {difficulty}

    Rules:

    1. Return only questions.
    2. One question per line.
    3. No numbering.
    4. No explanations.
    """

    try:

        response = gemini_model.generate_content(
            prompt
        )

        questions = [
            q.strip()
            for q in response.text.split("\n")
            if q.strip()
        ]

        return questions

    except Exception as e:

        print("Gemini Error:", e)

        return [
            "Tell me about yourself."
        ]


# =====================================================
# GEMINI ANSWER EVALUATOR
# =====================================================

def evaluate_answer(
    question,
    answer
):
    """
    Evaluate answer using Gemini
    """

    prompt = f"""
    Interview Question:
    {question}

    Candidate Answer:
    {answer}

    Evaluate answer.

    Return JSON:

    {{
      "score": 0-100,
      "feedback": "feedback text"
    }}
    """

    try:

        response = gemini_model.generate_content(
            prompt
        )

        text = response.text

        start = text.find("{")
        end = text.rfind("}")

        json_text = text[start:end + 1]

        result = json.loads(
            json_text
        )

        return result

    except Exception as e:

        print("Evaluation Error:", e)

        return {
            "score": 50,
            "feedback":
            "Unable to evaluate answer."
        }

# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template(
        "index.html"
    )


# =====================================================
# REGISTER
# =====================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name"
        )

        email = request.form.get(
            "email"
        ).strip().lower()

        password = request.form.get(
            "password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        if (
            not full_name
            or not email
            or not password
        ):

            flash(
                "Please fill all fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if (
            len(password)
            <
            app.config[
                "MIN_PASSWORD_LENGTH"
            ]
        ):

            flash(
                f"Password must be at least "
                f"{app.config['MIN_PASSWORD_LENGTH']} characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        connection = get_db_connection()

        if not connection:

            flash(
                "Database connection failed.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()
            connection.close()

            flash(
                "Email already exists.",
                "warning"
            )

            return redirect(
                url_for("register")
            )

        hashed_password = generate_password_hash(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (
                full_name,
                email,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                full_name,
                email,
                hashed_password
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =====================================================
# LOGIN
# =====================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email"
        ).strip().lower()

        password = request.form.get(
            "password"
        )

        connection = get_db_connection()

        if not connection:

            flash(
                "Database connection failed.",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if (
            user
            and
            check_password_hash(
                user["password"],
                password
            )
        ):

            session["user_id"] = user["id"]

            session["user_name"] = (
                user["full_name"]
            )

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(
        url_for("login")
    )

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("logout")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    # ==========================================
    # USER STATISTICS
    # ==========================================

    cursor.execute(
        """
        SELECT
            total_interviews,
            highest_score,
            average_score
        FROM user_statistics
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    statistics = cursor.fetchone()

    if not statistics:

        statistics = {
            "total_interviews": 0,
            "highest_score": 0,
            "average_score": 0
        }

    # ==========================================
    # RECENT INTERVIEWS
    # ==========================================

    cursor.execute(
        """
        SELECT
            id,
            role,
            difficulty,
            score,
            status,
            created_at
        FROM interviews
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (session["user_id"],)
    )

    recent_interviews = cursor.fetchall()

    # ==========================================
    # CHART DATA
    # ==========================================

    cursor.execute(
        """
        SELECT
            role,
            score
        FROM interviews
        WHERE user_id = %s
        AND status = 'Completed'
        ORDER BY created_at ASC
        """,
        (session["user_id"],)
    )

    chart_rows = cursor.fetchall()

    chart_labels = []
    chart_scores = []

    for row in chart_rows:

        chart_labels.append(
            row["role"]
        )

        chart_scores.append(
            row["score"]
        )

    # ==========================================
    # ROLE DISTRIBUTION
    # ==========================================

    cursor.execute(
        """
        SELECT
            role,
            COUNT(*) as total
        FROM interviews
        WHERE user_id = %s
        GROUP BY role
        """,
        (session["user_id"],)
    )

    role_data = cursor.fetchall()

    role_labels = []
    role_counts = []

    for role in role_data:

        role_labels.append(
            role["role"]
        )

        role_counts.append(
            role["total"]
        )

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",

        user=user,

        statistics=statistics,

        recent_interviews=recent_interviews,

        chart_labels=chart_labels,

        chart_scores=chart_scores,

        role_labels=role_labels,

        role_counts=role_counts
    )


# =====================================================
# UPDATE USER STATISTICS
# =====================================================

def update_user_statistics(user_id):

    connection = get_db_connection()

    if not connection:
        return

    cursor = connection.cursor(
        dictionary=True
    )

    # Total Interviews

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM interviews
        WHERE user_id = %s
        AND status = 'Completed'
        """,
        (user_id,)
    )

    total_interviews = cursor.fetchone()[
        "total"
    ]

    # Highest Score

    cursor.execute(
        """
        SELECT MAX(score) AS highest
        FROM interviews
        WHERE user_id = %s
        AND status = 'Completed'
        """,
        (user_id,)
    )

    highest_score = cursor.fetchone()[
        "highest"
    ]

    if highest_score is None:
        highest_score = 0

    # Average Score

    cursor.execute(
        """
        SELECT AVG(score) AS average_score
        FROM interviews
        WHERE user_id = %s
        AND status = 'Completed'
        """,
        (user_id,)
    )

    avg_score = cursor.fetchone()[
        "average_score"
    ]

    if avg_score is None:
        avg_score = 0

    # Update Table

    cursor.execute(
        """
        UPDATE user_statistics
        SET
            total_interviews = %s,
            highest_score = %s,
            average_score = %s
        WHERE user_id = %s
        """,
        (
            total_interviews,
            highest_score,
            round(avg_score, 2),
            user_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

# =====================================================
# START INTERVIEW
# =====================================================

@app.route(
    "/start-interview",
    methods=["POST"]
)
@login_required
def start_interview():

    role = request.form.get(
        "role"
    )

    difficulty = request.form.get(
        "difficulty"
    )

    total_questions = int(
        request.form.get(
            "total_questions",
            5
        )
    )

    # Generate Questions Using Gemini

    questions = generate_interview_questions(
        role,
        difficulty,
        total_questions
    )

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    cursor = connection.cursor()

    # Create Interview

    cursor.execute(
        """
        INSERT INTO interviews
        (
            user_id,
            role,
            difficulty,
            total_questions,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            'In Progress'
        )
        """,
        (
            session["user_id"],
            role,
            difficulty,
            total_questions
        )
    )

    interview_id = cursor.lastrowid

    # Store Questions

    for question in questions:

        cursor.execute(
            """
            INSERT INTO questions
            (
                interview_id,
                question_text
            )
            VALUES
            (
                %s,
                %s
            )
            """,
            (
                interview_id,
                question
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        url_for(
            "interview",
            interview_id=interview_id
        )
    )


# =====================================================
# INTERVIEW PAGE
# =====================================================

@app.route(
    "/interview/<int:interview_id>"
)
@login_required
def interview(interview_id):

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    # Verify Ownership

    cursor.execute(
        """
        SELECT *
        FROM interviews
        WHERE id = %s
        AND user_id = %s
        """,
        (
            interview_id,
            session["user_id"]
        )
    )

    interview_data = cursor.fetchone()

    if not interview_data:

        cursor.close()
        connection.close()

        flash(
            "Interview not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    # Fetch Questions

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE interview_id = %s
        ORDER BY id ASC
        """,
        (interview_id,)
    )

    questions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "interview.html",
        interview=interview_data,
        questions=questions,
        total_questions=len(questions)
    )


# =====================================================
# SAVE ANSWER
# =====================================================

@app.route(
    "/save-answer",
    methods=["POST"]
)
@login_required
def save_answer():

    question_id = request.form.get(
        "question_id"
    )

    answer = request.form.get(
        "answer"
    )

    connection = get_db_connection()

    if not connection:

        return jsonify(
            {
                "success": False,
                "message":
                "Database connection failed"
            }
        )

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE questions
        SET answer_text = %s
        WHERE id = %s
        """,
        (
            answer,
            question_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify(
        {
            "success": True
        }
    )


# =====================================================
# LOAD INTERVIEW QUESTIONS API
# =====================================================

@app.route(
    "/api/interview/<int:interview_id>"
)
@login_required
def interview_api(interview_id):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            question_text,
            answer_text
        FROM questions
        WHERE interview_id = %s
        ORDER BY id ASC
        """,
        (interview_id,)
    )

    questions = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(
        questions
    )

# =====================================================
# SUBMIT INTERVIEW
# =====================================================

@app.route(
    "/submit-interview/<int:interview_id>",
    methods=["POST"]
)
@login_required
def submit_interview(interview_id):

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    # ==========================================
    # VERIFY INTERVIEW OWNERSHIP
    # ==========================================

    cursor.execute(
        """
        SELECT *
        FROM interviews
        WHERE id = %s
        AND user_id = %s
        """,
        (
            interview_id,
            session["user_id"]
        )
    )

    interview = cursor.fetchone()

    if not interview:

        cursor.close()
        connection.close()

        flash(
            "Interview not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    # ==========================================
    # FETCH QUESTIONS
    # ==========================================

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE interview_id = %s
        ORDER BY id ASC
        """,
        (interview_id,)
    )

    questions = cursor.fetchall()

    total_score = 0

    strengths = []
    weaknesses = []
    suggestions = []

    # ==========================================
    # EVALUATE EACH ANSWER
    # ==========================================

    for question in questions:

        answer = (
            question["answer_text"]
            if question["answer_text"]
            else "No Answer Provided"
        )

        result = evaluate_answer(
            question["question_text"],
            answer
        )

        score = int(
            result.get(
                "score",
                0
            )
        )

        feedback = result.get(
            "feedback",
            "No feedback generated."
        )

        total_score += score

        cursor.execute(
            """
            UPDATE questions
            SET
                question_score = %s,
                ai_feedback = %s
            WHERE id = %s
            """,
            (
                score,
                feedback,
                question["id"]
            )
        )

    # ==========================================
    # CALCULATE FINAL SCORE
    # ==========================================

    if len(questions) > 0:

        overall_score = round(
            total_score /
            len(questions)
        )

    else:

        overall_score = 0

    # ==========================================
    # GENERATE REPORT USING GEMINI
    # ==========================================

    report_prompt = f"""
    Generate a professional interview report.

    Interview Role:
    {interview['role']}

    Difficulty:
    {interview['difficulty']}

    Overall Score:
    {overall_score}

    Provide:

    1. Strengths
    2. Weaknesses
    3. Suggestions
    4. Summary

    Return JSON only.

    Example:

    {{
        "strengths":"...",
        "weaknesses":"...",
        "suggestions":"...",
        "summary":"..."
    }}
    """

    try:

        report_response = (
            gemini_model.generate_content(
                report_prompt
            )
        )

        report_text = (
            report_response.text
        )

        start = report_text.find("{")
        end = report_text.rfind("}")

        report_json = json.loads(
            report_text[start:end+1]
        )

        strengths = report_json.get(
            "strengths",
            ""
        )

        weaknesses = report_json.get(
            "weaknesses",
            ""
        )

        suggestions = report_json.get(
            "suggestions",
            ""
        )

        summary = report_json.get(
            "summary",
            ""
        )

    except Exception as e:

        print(
            "Report Error:",
            e
        )

        strengths = (
            "Good effort."
        )

        weaknesses = (
            "Needs improvement."
        )

        suggestions = (
            "Practice more interviews."
        )

        summary = (
            "Report generation failed."
        )

    # ==========================================
    # UPDATE INTERVIEW
    # ==========================================

    cursor.execute(
        """
        UPDATE interviews
        SET
            score = %s,
            status = 'Completed'
        WHERE id = %s
        """,
        (
            overall_score,
            interview_id
        )
    )

    # ==========================================
    # SAVE REPORT
    # ==========================================

    cursor.execute(
        """
        INSERT INTO reports
        (
            interview_id,
            overall_score,
            strengths,
            weaknesses,
            suggestions,
            report_summary
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            interview_id,
            overall_score,
            strengths,
            weaknesses,
            suggestions,
            summary
        )
    )

    connection.commit()

    # ==========================================
    # UPDATE USER STATS
    # ==========================================

    update_user_statistics(
        session["user_id"]
    )

    cursor.close()
    connection.close()

    flash(
        "Interview evaluated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "report",
            interview_id=interview_id
        )
    )


# =====================================================
# GENERATE REPORT API
# =====================================================

@app.route(
    "/api/report/<int:interview_id>"
)
@login_required
def report_api(interview_id):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM reports
        WHERE interview_id = %s
        """,
        (interview_id,)
    )

    report = cursor.fetchone()

    cursor.close()
    connection.close()

    if not report:

        return jsonify(
            {
                "success": False
            }
        )

    return jsonify(
        {
            "success": True,
            "report": report
        }
    )

# =====================================================
# REPORT PAGE
# =====================================================

@app.route(
    "/report/<int:interview_id>"
)
@login_required
def report(interview_id):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            r.*,
            i.role,
            i.difficulty,
            i.created_at
        FROM reports r
        JOIN interviews i
        ON r.interview_id = i.id
        WHERE r.interview_id = %s
        AND i.user_id = %s
        """,
        (
            interview_id,
            session["user_id"]
        )
    )

    report_data = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            question_text,
            answer_text,
            ai_feedback,
            question_score
        FROM questions
        WHERE interview_id = %s
        ORDER BY id ASC
        """,
        (interview_id,)
    )

    questions = cursor.fetchall()

    cursor.close()
    connection.close()

    if not report_data:

        flash(
            "Report not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "report.html",
        report=report_data,
        questions=questions
    )


# =====================================================
# INTERVIEW HISTORY
# =====================================================

@app.route("/history")
@login_required
def history():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM interviews
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )

    interviews = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "history.html",
        interviews=interviews
    )


# =====================================================
# DELETE INTERVIEW
# =====================================================

@app.route(
    "/delete-interview/<int:interview_id>",
    methods=["POST"]
)
@login_required
def delete_interview(interview_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM interviews
        WHERE id = %s
        AND user_id = %s
        """,
        (
            interview_id,
            session["user_id"]
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    update_user_statistics(
        session["user_id"]
    )

    flash(
        "Interview deleted successfully.",
        "success"
    )

    return redirect(
        url_for("history")
    )


# =====================================================
# USER PROFILE
# =====================================================

@app.route("/profile")
@login_required
def profile():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM user_statistics
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    statistics = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "profile.html",
        user=user,
        statistics=statistics
    )


# =====================================================
# UPDATE PROFILE
# =====================================================

@app.route(
    "/update-profile",
    methods=["POST"]
)
@login_required
def update_profile():

    full_name = request.form.get(
        "full_name"
    )

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET full_name = %s
        WHERE id = %s
        """,
        (
            full_name,
            session["user_id"]
        )
    )

    connection.commit()

    session["user_name"] = full_name

    cursor.close()
    connection.close()

    flash(
        "Profile updated successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# =====================================================
# CHANGE PASSWORD
# =====================================================

@app.route(
    "/change-password",
    methods=["POST"]
)
@login_required
def change_password():

    current_password = request.form.get(
        "current_password"
    )

    new_password = request.form.get(
        "new_password"
    )

    confirm_password = request.form.get(
        "confirm_password"
    )

    if new_password != confirm_password:

        flash(
            "Passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT password
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    if not check_password_hash(
        user["password"],
        current_password
    ):

        cursor.close()
        connection.close()

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    hashed_password = generate_password_hash(
        new_password
    )

    cursor.execute(
        """
        UPDATE users
        SET password = %s
        WHERE id = %s
        """,
        (
            hashed_password,
            session["user_id"]
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash(
        "Password changed successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# =====================================================
# RESUME UPLOAD
# =====================================================

@app.route(
    "/upload-resume",
    methods=["POST"]
)
@login_required
def upload_resume():

    if "resume" not in request.files:

        flash(
            "No file selected.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    file = request.files["resume"]

    if file.filename == "":

        flash(
            "No file selected.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if not allowed_file(file.filename):

        flash(
            "Only PDF, DOC and DOCX files are allowed.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    filename = secure_filename(
        file.filename
    )

    save_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(save_path)

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO resumes
        (
            user_id,
            resume_filename
        )
        VALUES
        (
            %s,
            %s
        )
        """,
        (
            session["user_id"],
            filename
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash(
        "Resume uploaded successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# =====================================================
# PERSONALIZED QUESTIONS
# =====================================================

@app.route(
    "/generate-personalized-questions/<int:resume_id>"
)
@login_required
def generate_personalized_questions(
    resume_id
):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM resumes
        WHERE id = %s
        AND user_id = %s
        """,
        (
            resume_id,
            session["user_id"]
        )
    )

    resume = cursor.fetchone()

    cursor.close()
    connection.close()

    if not resume:

        return jsonify(
            {
                "success": False,
                "message": "Resume not found"
            }
        )

    prompt = f"""
    Generate 10 interview questions
    based on this resume.

    Resume File:
    {resume['resume_filename']}

    Focus on:
    Skills
    Projects
    Experience

    Return only questions.
    """

    try:

        response = gemini_model.generate_content(
            prompt
        )

        questions = [
            q.strip()
            for q in response.text.split("\n")
            if q.strip()
        ]

        return jsonify(
            {
                "success": True,
                "questions": questions
            }
        )

    except Exception as e:

        return jsonify(
            {
                "success": False,
                "message": str(e)
            }
        )


# =====================================================
# GLOBAL ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "500.html"
    ), 500


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health")
def health_check():

    return jsonify(
        {
            "status": "ok",
            "application": "InterviewAce AI",
            "timestamp": str(
                datetime.now()
            )
        }
    )


# =====================================================
# CONTEXT PROCESSOR
# =====================================================

@app.context_processor
def inject_user():

    return {
        "current_user":
        get_current_user()
    }


# =====================================================
# BEFORE REQUEST
# =====================================================

@app.before_request
def before_request():

    session.permanent = True


# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config["DEBUG"]
    )

