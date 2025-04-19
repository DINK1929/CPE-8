import sqlite3

conn = sqlite3.connect('malin_ease.db')
cursor = conn.cursor()

# --- Drop & Recreate Tables for Development ---
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("DROP TABLE IF EXISTS teachers")
cursor.execute("DROP TABLE IF EXISTS vouchers")
cursor.execute("DROP TABLE IF EXISTS ratings")  # Drop the ratings table if it exists

# --- Create tables ---
cursor.execute('''
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_id TEXT UNIQUE,
    name TEXT,
    section TEXT,
    points INTEGER DEFAULT 0,
    cleaning_day TEXT
)
''')

cursor.execute('''
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY,
    teacher_id TEXT UNIQUE,
    name TEXT,
    section TEXT
)
''')

cursor.execute('''
CREATE TABLE vouchers (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    status TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

# Create the ratings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    groupmate_id TEXT,
    rating INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (groupmate_id) REFERENCES students(student_id)
)
''')

# --- Sample data ---
sample_students = [
    ('0323-2034', 'John Ernest Rod P. Andal', 'Monday'),
    ('0323-2035', 'Gilbert Paul Andrei P. Aragones', 'Monday'),
    ('0323-2036', 'Ronald Aspuria', 'Monday'),
    ('0323-2037', 'Josh Gabriel D. Austria', 'Monday'),
    ('0323-2038', 'Lance Justine P. Bunquin', 'Monday'),
    ('0324-0654', 'Prince John F. Castillo', 'Monday'),
    ('0323-2039', 'Eve Nonjon A. Concordia', 'Tuesday'),
    ('0323-2040', 'John Clarence C. Coroza', 'Tuesday'),
    ('0323-2041', 'Dirk Justine F. Cuenca', 'Tuesday'),
    ('0323-2042', 'Cyrene E. Del Mundo', 'Tuesday'),
    ('0323-2044', 'Steven Kirby T. Dichoso', 'Tuesday'),
    ('0323-2045', 'Pierre Andrei F. Escalona', 'Tuesday'),
    ('0323-2047', 'Raizen B. Lauron', 'Wednesday'),
    ('0323-2048', 'James Adrian C. Malabanan', 'Wednesday'),
    ('0323-2049', 'Jiro A. Medrano', 'Wednesday'),
    ('0323-2050', 'Vanessa Nicole G. Meer', 'Wednesday'),
    ('0323-2051', 'Benj B. Monesia', 'Wednesday'),
    ('0323-2052', 'James Samuel B. Navera', 'Thursday'),
    ('0323-2053', 'Ryza Mae B. Peñafiel', 'Thursday'),
    ('0323-2346', 'Ramil B. Pontalba JR.', 'Thursday'),
    ('0323-2054', 'Chrizhelle Mae A. Pulla', 'Thursday'),
    ('0321-3621', 'Selwyn B. Retirado', 'Thursday'),
    ('0323-4661', 'Dan Carl B. Solayao', 'Friday'),
    ('0323-4325', 'Renzter Luis S. Suarez', 'Friday'),
    ('0323-2056', 'Jeaddeah F. Suministrado', 'Friday'),
    ('0323-4533', 'Derick Emmanuel R. Torbela', 'Friday'),
    ('0323-2058', 'Sachi L. Vispo', 'Friday')
]

# Insert into the database with the cleaning day
for student_id, name, cleaning_day in sample_students:
    cursor.execute("INSERT OR IGNORE INTO students (student_id, name, section, points, cleaning_day) VALUES (?, ?, ?, ?, ?)",
                   (student_id, name, 'BSCPE 2B', 0, cleaning_day))

conn.commit()

# Insert teacher data
cursor.execute("INSERT OR IGNORE INTO teachers (teacher_id, name, section) VALUES (?, ?, ?)",
               ('0320-1025', 'Shaira Mae Bughaw', 'BSCPE 2B'))
conn.commit()

# --- Database Functions ---
def insert_student(student_id, name, section, cleaning_day, points):
    cursor.execute("INSERT OR IGNORE INTO students (student_id, name, section, cleaning_day) VALUES (?, ?, ?, ?, ?)",
                   (student_id, name, section, cleaning_day, points))
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
    return cursor.fetchone()

def assign_cleaning_day(student_id, day):
    cursor.execute("UPDATE students SET cleaning_day = ? WHERE student_id = ?", (day, student_id))
    conn.commit()

def get_teacher_info(teacher_id):
    cursor.execute("SELECT name, section FROM teachers WHERE teacher_id = ?", (teacher_id,))
    return cursor.fetchone()

def section_exists(section):
    cursor.execute("SELECT 1 FROM students WHERE section = ? LIMIT 1", (section,))
    student_exists = cursor.fetchone()
    cursor.execute("SELECT 1 FROM teachers WHERE section = ? LIMIT 1", (section,))
    teacher_exists = cursor.fetchone()
    return student_exists or teacher_exists

# --- Ratings Functions ---
def insert_rating(student_id, groupmate_id, rating):
    cursor.execute("INSERT INTO ratings (student_id, groupmate_id, rating) VALUES (?, ?, ?)",
                   (student_id, groupmate_id, rating))
    conn.commit()

def get_ratings_for_student(student_id):
    cursor.execute("SELECT groupmate_id, rating FROM ratings WHERE student_id = ?", (student_id,))
    return cursor.fetchall()

def get_average_rating(student_id):
    cursor.execute("SELECT AVG(rating) FROM ratings WHERE groupmate_id = ?", (student_id,))
    return cursor.fetchone()[0] or 0
