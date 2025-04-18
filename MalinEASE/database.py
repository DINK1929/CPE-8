import sqlite3

conn = sqlite3.connect('malin_ease.db')
cursor = conn.cursor()

# --- Drop & Recreate Tables for Development (avoids schema mismatch) ---
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("DROP TABLE IF EXISTS teachers")
cursor.execute("DROP TABLE IF EXISTS vouchers")
cursor.execute("DROP TABLE IF EXISTS ratings")

# --- Create tables with name fields ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    student_id TEXT UNIQUE,
    name TEXT,
    section TEXT,
    points INTEGER DEFAULT 0,
    cleaning_day TEXT
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

cursor.execute('''
CREATE TABLE IF NOT EXISTS ratings (
    rater_id TEXT,
    ratee_id TEXT,
    score INTEGER,
    section TEXT,
    PRIMARY KEY (rater_id, ratee_id),
    FOREIGN KEY (rater_id) REFERENCES students(student_id),
    FOREIGN KEY (ratee_id) REFERENCES students(student_id)
)
''')

# --- Add sample data ---
sample_students = [
    ('0323-2034', 'John Ernest Rod P. Andal'),
    ('0323-2035', 'Gilbert Paul Andrei P. Aragones'),
    ('0323-2036', 'Ronald Aspuria'),
    ('0323-2037', 'Josh Gabriel D. Austria'),
    ('0323-2038', 'Lance Justine P. Bunquin'),
    ('0324-0654', 'Prince John F. Castillo'),
    ('0323-2039', 'Eve Nonjon A. Concordia'),
    ('0323-2040', 'John Clarence C. Coroza'),
    ('0323-2041', 'Dirk justine F. Cuenca'),
    ('0323-2042', 'Cyrene E. Del Mundo'),
    ('0323-2044', 'Steven Kirby T. Dichoso'),
    ('0323-2045', 'Pierre Andrei F. Escalona'),
    ('0323-2047', 'Raizen B. Lauron'),
    ('0323-2048', 'James Adrian C. Malabanan'),
    ('0323-2049', 'Jiro A. Medrano'),
    ('0323-2050', 'Vanessa Nicole G. Meer'),
    ('0323-2051', 'Benj B. Monesia'),
    ('0323-2052', 'James Samuel B. navera'),
    ('0323-2053', 'Ryza Mae B. Peñafiel'),
    ('0323-2346', 'Ramil B. Pontalba JR.'),
    ('0323-2054', 'Chrizhelle Mae A. Pulla'),
    ('0321-3621', 'Selwyn B. Retirado'),
    ('0323-4661', 'Dan Carl B. Solayao'),
    ('0323-4325', 'Renzter Luis S. Suarez'),
    ('0323-2056', 'Jeaddeah F. Suministrado'),
    ('0323-4533', 'Derick Emmanuel R. Torbela'),
    ('0323-2058', 'Sachi L. Vispo')
]

for student_id, name in sample_students:
    cursor.execute("INSERT OR IGNORE INTO students (student_id, name, section, points) VALUES (?, ?, ?, ?)",
                   (student_id, name, 'BSCPE 2B', 0))

cursor.execute("INSERT OR IGNORE INTO teachers (teacher_id, name, section) VALUES (?, ?, ?)",
               ('0320-1025', 'Shaira Mae Bughaw', 'BSCPE 2B'))

# --- Step 2: Assign cleaning days permanently ---
cursor.execute("SELECT student_id FROM students ORDER BY student_id")
all_students = cursor.fetchall()
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

for index, (student_id,) in enumerate(all_students):
    assigned_day = days[index % 5]
    cursor.execute("UPDATE students SET cleaning_day = ? WHERE student_id = ?", (assigned_day, student_id))

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
    cursor.execute("SELECT 1 FROM students WHERE section = ? LIMIT 1", (section,))
    student_exists = cursor.fetchone()
    cursor.execute("SELECT 1 FROM teachers WHERE section = ? LIMIT 1", (section,))
    teacher_exists = cursor.fetchone()
    return student_exists or teacher_exists

# --- Rating System Functions ---
def submit_ratings(rater_id, section, ratings_dict):
    for ratee_id, score in ratings_dict.items():
        cursor.execute('''
            INSERT OR REPLACE INTO ratings (rater_id, ratee_id, score, section)
            VALUES (?, ?, ?, ?)
        ''', (rater_id, ratee_id, score, section))
    conn.commit()

def update_points_from_ratings(section):
    cursor.execute('''
        SELECT ratee_id, AVG(score) as avg_score
        FROM ratings
        WHERE section = ?
        GROUP BY ratee_id
    ''', (section,))
    results = cursor.fetchall()

    for ratee_id, avg_score in results:
        points = int(round(avg_score))  # Simple mapping: 1 point = 1 avg rating
        cursor.execute('UPDATE students SET points = ? WHERE student_id = ?', (points, ratee_id))

    conn.commit()
