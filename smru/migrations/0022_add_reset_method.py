from django.db import migrations, connection


def add_reset_method_column(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(smru_passwordresetrequest);")
        cols = [r[1] for r in cursor.fetchall()]
        if 'reset_method' not in cols:
            # Add column with default to avoid NOT NULL issues
            cursor.execute("ALTER TABLE smru_passwordresetrequest ADD COLUMN reset_method VARCHAR(20) DEFAULT 'email';")


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ('smru', '0021_alter_userrole_user'),
    ]

    operations = [
        migrations.RunPython(add_reset_method_column, reverse_code=noop),
    ]
