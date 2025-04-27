import sqlite3

# --- Database Setup ---
conn = sqlite3.connect('malin_ease.db')
cursor = conn.cursor()

# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

# Create tables with IF NOT EXISTS
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    name TEXT,
    section TEXT,
    rating INTEGER DEFAULT 0,
    cleaning_day TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT UNIQUE,
    name TEXT,
    section TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vouchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    voucher_type TEXT,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rated_by TEXT,
    student_id TEXT,
    rating INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

# --- Insert Sample Data ---
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

for student_id, name, cleaning_day in sample_students:
    cursor.execute('''
        INSERT OR IGNORE INTO students (student_id, name, section, rating, cleaning_day)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_id, name, 'BSCPE 2B', 0, cleaning_day))

# Insert sample teacher
cursor.execute('''
    INSERT OR IGNORE INTO teachers (teacher_id, name, section)
    VALUES (?, ?, ?)
''', ('0320-1025', 'Shaira Mae Bughaw', 'BSCPE 2B'))

conn.commit()

# --- Database Functions ---
def get_student_info(student_id):
    cursor.execute('SELECT name, section, rating FROM students WHERE student_id = ?', (student_id,))
    return cursor.fetchone()

def get_teacher_info(teacher_id):
    cursor.execute('SELECT name, section FROM teachers WHERE teacher_id = ?', (teacher_id,))
    return cursor.fetchone()

def section_exists(section):
    cursor.execute('SELECT 1 FROM students WHERE section = ? LIMIT 1', (section,))
    if cursor.fetchone():
        return True
    cursor.execute('SELECT 1 FROM teachers WHERE section = ? LIMIT 1', (section,))
    return bool(cursor.fetchone())

def create_voucher(student_id, voucher_type):
    cursor.execute('''
        INSERT INTO vouchers (student_id, voucher_type)
        VALUES (?, ?)
    ''', (student_id, voucher_type))
    conn.commit()

def get_pending_vouchers():
    cursor.execute('''
        SELECT v.id, s.name, v.voucher_type
        FROM vouchers v
        JOIN students s ON v.student_id = s.student_id
        WHERE v.status = 'pending'
    ''')
    return cursor.fetchall()

def approve_voucher(voucher_id):
    cursor.execute('SELECT student_id, voucher_type FROM vouchers WHERE id = ?', (voucher_id,))
    voucher = cursor.fetchone()
    if not voucher:
        return False

    student_id, voucher_type = voucher

    if voucher_type == 'skip_cleaning':
        cursor.execute('''
            UPDATE students
            SET cleaning_day = 'skip', rating = rating - 20
            WHERE student_id = ?
        ''', (student_id,))

    cursor.execute('UPDATE vouchers SET status = "approved" WHERE id = ?', (voucher_id,))
    conn.commit()
    return True

def reject_voucher(voucher_id):
    cursor.execute('UPDATE vouchers SET status = "rejected" WHERE id = ?', (voucher_id,))
    conn.commit()

def can_purchase_voucher(student_id, voucher_type):
    cursor.execute('SELECT rating FROM students WHERE student_id = ?', (student_id,))
    result = cursor.fetchone()
    if not result:
        return False

    current_rating = result[0]
    voucher_costs = {'skip_cleaning': 20}
    cost = voucher_costs.get(voucher_type)
    if cost is None:
        return False
    return current_rating >= cost

# Add these new functions to database.py

def get_student_vouchers(student_id):
    """Get all vouchers for a specific student with their status"""
    cursor.execute("""
        SELECT id, voucher_type, status 
        FROM vouchers 
        WHERE student_id = ?
        ORDER BY id DESC
    """, (student_id,))
    return cursor.fetchall()

def get_voucher_status(voucher_id):
    """Get status of a specific voucher"""
    cursor.execute("SELECT status FROM vouchers WHERE id = ?", (voucher_id,))
    result = cursor.fetchone()
    return result[0] if result else None