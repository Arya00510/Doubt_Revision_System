from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def init_db():

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    # -------------------------------------------------
    # DOUBTS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            chapter TEXT,
            topic TEXT,
            doubt TEXT
        )
    """)

    # Add status column to existing doubts table
    try:
        cursor.execute(
            "ALTER TABLE doubts ADD COLUMN status TEXT DEFAULT 'Pending'"
        )
    except sqlite3.OperationalError:
        pass

    # Make old doubts Pending
    cursor.execute("""
        UPDATE doubts
        SET status = 'Pending'
        WHERE status IS NULL
    """)


    # -------------------------------------------------
    # SESSIONS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            topic TEXT,
            date TEXT,
            time TEXT,
            room TEXT,
            notes TEXT
        )
    """)

    # Add chapter column to existing sessions table
    try:
        cursor.execute(
            "ALTER TABLE sessions ADD COLUMN chapter TEXT"
        )
    except sqlite3.OperationalError:
        pass


    # -------------------------------------------------
    # USERS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            name TEXT,
            password TEXT,
            role TEXT,
            subject TEXT
        )
    """)


    # -------------------------------------------------
    # DEMO USERS
    # -------------------------------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, name, password, role, subject)
        VALUES
        ('STU001', 'Arya', 'student123', 'Student', ''),
        ('STU002', 'Rahul', 'student123', 'Student', ''),
        ('TCH001', 'Mrs.Ashwini', 'teacher123', 'Teacher', 'Data Structures')
    """)


    conn.commit()
    conn.close()


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# STUDENT LOGIN
# =====================================================

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        user_id = request.form["user_id"]
        password = request.form["password"]

        conn = sqlite3.connect("doubts.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, role
            FROM users
            WHERE user_id = ?
            AND password = ?
            AND role = 'Student'
        """, (user_id, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            return render_template(
                "student_dashboard.html",
                name=user[0]
            )

        return render_template(
            "student_login.html",
            error="Invalid Student ID or Password"
        )

    return render_template("student_login.html")


# =====================================================
# STUDENT DASHBOARD
# =====================================================

@app.route("/student-dashboard")
def student_dashboard():

    return render_template(
        "student_dashboard.html"
    )


# =====================================================
# STUDENT REVISION SESSION
# =====================================================

@app.route("/student-revision")
def student_revision():

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM sessions
        ORDER BY id DESC
        LIMIT 1
    """)

    session = cursor.fetchone()

    conn.close()

    return render_template(
        "student_revision.html",
        session=session
    )


# =====================================================
# MY DOUBTS
# =====================================================

@app.route("/my-doubts")
def my_doubts():

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM doubts
    """)

    doubts = cursor.fetchall()

    conn.close()

    return render_template(
        "my_doubts.html",
        doubts=doubts
    )


# =====================================================
# DOUBT DETAILS
# =====================================================

@app.route("/doubt/<int:doubt_id>")
def doubt_details(doubt_id):

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM doubts WHERE id = ?",
        (doubt_id,)
    )

    doubt = cursor.fetchone()

    conn.close()

    return render_template(
        "doubt_details.html",
        doubt=doubt
    )


# =====================================================
# SUBMIT DOUBT
# =====================================================

@app.route("/submit-doubt", methods=["GET", "POST"])
def submit_doubt():

    if request.method == "POST":

        subject = request.form["subject"]
        chapter = request.form["chapter"]
        topic = request.form["topic"]
        doubt = request.form.get("doubt", "")

        conn = sqlite3.connect("doubts.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO doubts
            (subject, chapter, topic, doubt, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            subject,
            chapter,
            topic,
            doubt,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return render_template(
            "success.html"
        )

    return render_template(
        "submit_doubt.html"
    )


# =====================================================
# TEACHER LOGIN
# =====================================================

@app.route("/teacher-login")
def teacher_login():

    return render_template(
        "teacher_login.html"
    )


# =====================================================
# TEACHER DASHBOARD
# =====================================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    return render_template(
        "teacher_dashboard.html"
    )


# =====================================================
# TEACHER PROFILE
# =====================================================

@app.route("/profile")
def profile():

    return render_template(
        "profile.html"
    )


# =====================================================
# TEACHER DOUBTS
# =====================================================

@app.route("/teacher-doubts")
def teacher_doubts():

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM doubts
        WHERE subject = ?
    """, ("Data Structures",))

    doubts = cursor.fetchall()

    conn.close()

    return render_template(
        "teacher_doubts.html",
        doubts=doubts
    )


# =====================================================
# UPDATE DOUBT STATUS
# =====================================================

@app.route("/update-doubt-status/<int:doubt_id>", methods=["POST"])
def update_doubt_status(doubt_id):

    status = request.form["status"]

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE doubts
        SET status = ?
        WHERE id = ?
    """, (status, doubt_id))

    conn.commit()
    conn.close()

    return redirect("/teacher-doubts")


# =====================================================
# COMMON DOUBTS
# =====================================================

@app.route("/common-doubts")
def common_doubts():

    conn = sqlite3.connect("doubts.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT chapter, topic, COUNT(*)
        FROM doubts
        WHERE subject = ?
        GROUP BY chapter, topic
        ORDER BY COUNT(*) DESC
    """, ("Data Structures",))

    common_doubts = cursor.fetchall()

    conn.close()

    return render_template(
        "common_doubts.html",
        common_doubts=common_doubts
    )


# =====================================================
# SCHEDULE REVISION
# =====================================================

@app.route("/schedule-revision", methods=["GET", "POST"])
def schedule_revision():

    if request.method == "POST":

        subject = request.form["subject"]
        chapter = request.form["chapter"]
        topic = request.form["topic"]
        date = request.form["date"]
        time = request.form["time"]
        room = request.form["room"]
        notes = request.form.get("notes", "")

        conn = sqlite3.connect("doubts.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions
            (subject, chapter, topic, date, time, room, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            subject,
            chapter,
            topic,
            date,
            time,
            room,
            notes
        ))

        conn.commit()
        conn.close()

        return render_template(
            "schedule_revision.html",
            message="Revision session scheduled successfully!"
        )

    return render_template(
        "schedule_revision.html"
    )


# =====================================================
# INITIALIZE DATABASE
# =====================================================

init_db()


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

 app.run(debug=True)