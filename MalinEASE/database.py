import sqlite3

conn = sqlite3.connect('malin_ease.db')
cursor = conn.cursor()

# --- Drop & Recreate Tables for Development (avoids schema mismatch) ---
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("DROP TABLE IF EXISTS teachers")
cursor.execute("DROP TABLE IF EXISTS vouchers")

# --- Create tables with name fields ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    student_id TEXT UNIQUE,
    name TEXT,
    section TEXT,
    points INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY,
    teacher_id TEXT UNIQUE,
    name TEXT,
    section TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vouchers (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    status TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

# --- Add sample data ---
cursor.execute("INSERT OR IGNORE INTO students (student_id, name, section, points) VALUES (?, ?, ?, ?)",
               ('0323-2041', 'Dirk justine F. Cuenca', 'BSCPE 2B', 0))

cursor.execute("INSERT OR IGNORE INTO teachers (teacher_id, name, section) VALUES (?, ?, ?)",
               ('0320-1025', 'Shaira Mae Bughaw', 'BSCPE 2B'))

conn.commit()

# --- Database functions ---
def insert_student(student_id, name, section):
    cursor.execute("INSERT OR IGNORE INTO students (student_id, name, section) VALUES (?, ?, ?)",
                   (student_id, name, section))
    conn.commit()

def get_points(student_id):
    cursor.execute("SELECT points FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def update_points(student_id, points):
    cursor.execute("UPDATE students SET points = ? WHERE student_id = ?", (points, student_id))
    conn.commit()

def get_student_info(student_id):
    cursor.execute("SELECT name, section, points FROM students WHERE student_id = ?", (student_id,))
    return cursor.fetchone()  # (name, section, points)

def get_teacher_info(teacher_id):
    cursor.execute("SELECT name, section FROM teachers WHERE teacher_id = ?", (teacher_id,))
    return cursor.fetchone()  # (name, section)

def section_exists(section):
    cursor.execute("SELECT 1 FROM students WHERE LOWER(section) = LOWER(?) LIMIT 1", (section,))
    return cursor.fetchone() is not None