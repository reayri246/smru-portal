import sqlite3, shutil, sys

# Backup
shutil.copy('db.sqlite3', 'db.sqlite3.bak')
print('Backup created: db.sqlite3.bak')

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
try:
    c.execute("ALTER TABLE smru_registrationapprovalrequest ADD COLUMN last_reminder_at datetime")
    conn.commit()
    print('Added column last_reminder_at')
except Exception as e:
    print('ALTER TABLE skipped/error:', e)

try:
    c.execute("ALTER TABLE smru_registrationapprovalrequest ADD COLUMN verification_passed INTEGER NOT NULL DEFAULT 0")
    conn.commit()
    print('Added column verification_passed')
except Exception as e:
    print('verification_passed skipped/error:', e)

try:
    c.execute("ALTER TABLE smru_registrationapprovalrequest ADD COLUMN verification_details TEXT NOT NULL DEFAULT ''")
    conn.commit()
    print('Added column verification_details')
except Exception as e:
    print('verification_details skipped/error:', e)

cols = list(conn.execute("PRAGMA table_info('smru_registrationapprovalrequest')"))
print('PRAGMA table_info:')
for r in cols:
    print(r)
conn.close()
