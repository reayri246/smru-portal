import sqlite3, shutil

shutil.copy('db.sqlite3', 'db.sqlite3.pre_create_tables.bak')
print('Backup created: db.sqlite3.pre_create_tables.bak')

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

def table_exists(name):
    return bool(c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone())

# Create StudyMaterial
if not table_exists('smru_studymaterial'):
    c.execute('''
    CREATE TABLE smru_studymaterial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        file VARCHAR(100) NOT NULL,
        created_at DATETIME NOT NULL,
        branch_id BIGINT,
        college_id BIGINT,
        uploaded_by_id INTEGER,
        year_id BIGINT
    )
    ''')
    print('Created table smru_studymaterial')
else:
    print('Table smru_studymaterial already exists')

# Create StaffLockLog
if not table_exists('smru_stafflocklog'):
    c.execute('''
    CREATE TABLE smru_stafflocklog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        locked_at DATETIME NOT NULL,
        unlocked_at DATETIME,
        reason VARCHAR(200),
        locked_by_id INTEGER,
        staff_id INTEGER NOT NULL
    )
    ''')
    print('Created table smru_stafflocklog')
else:
    print('Table smru_stafflocklog already exists')

# Create ReminderLog
if not table_exists('smru_reminderlog'):
    c.execute('''
    CREATE TABLE smru_reminderlog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sent_at DATETIME NOT NULL,
        message TEXT,
        request_id INTEGER NOT NULL,
        to_staff_id INTEGER
    )
    ''')
    print('Created table smru_reminderlog')
else:
    print('Table smru_reminderlog already exists')

# Create RegistrationAuditLog
if not table_exists('smru_registrationauditlog'):
    c.execute('''
    CREATE TABLE smru_registrationauditlog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action VARCHAR(100) NOT NULL,
        timestamp DATETIME NOT NULL,
        details TEXT,
        performed_by_id INTEGER,
        request_id INTEGER NOT NULL
    )
    ''')
    print('Created table smru_registrationauditlog')
else:
    print('Table smru_registrationauditlog already exists')

# Create StaffPermission
if not table_exists('smru_staffpermission'):
    c.execute('''
    CREATE TABLE smru_staffpermission (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        permission VARCHAR(100) NOT NULL,
        user_id INTEGER NOT NULL
    )
    ''')
    # create unique index to enforce unique_together (user, permission)
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS smru_staffpermission_user_permission_uniq ON smru_staffpermission(user_id, permission)")
    print('Created table smru_staffpermission and unique index')
else:
    print('Table smru_staffpermission already exists')

conn.commit()
conn.close()
print('Done')
