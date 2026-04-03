# Django Migrations Guide for College Portal

## Overview

This guide explains how to work with Django migrations in the College Portal project.

## Migration Files

Migrations are stored in `smru/migrations/`. Each migration file represents a change to the database schema.

### Initial Migration
- `0001_initial.py` - Creates all initial models

## Creating New Migrations

When you modify models (add/remove/change fields), you need to create a migration.

### Step 1: Modify Models

Edit `smru/models.py`:
```python
class Notification(models.Model):
    # ... existing fields ...
    new_field = models.CharField(max_length=100)  # New field
```

### Step 2: Create Migration

```bash
python manage.py makemigrations
```

This creates a new migration file in `smru/migrations/`.

### Step 3: Review Migration

Check the generated migration file to ensure it's correct:
```bash
cat smru/migrations/000X_<migration_name>.py
```

### Step 4: Apply Migration

```bash
python manage.py migrate
```

## Common Migration Scenarios

### Adding a New Field

```python
# models.py
class College(models.Model):
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)  # New field
```

```bash
python manage.py makemigrations
python manage.py migrate
```

### Making a Field Required

```python
# models.py
class College(models.Model):
    # Before:
    # description = models.TextField(blank=True, null=True)
    
    # After:
    description = models.TextField(default='')
```

Migration will prompt for default values.

### Renaming a Field

```bash
python manage.py makemigrations --name rename_field_name
```

Edit the generated migration:
```python
# In the migration file:
migrations.RenameField(
    model_name='college',
    old_name='old_field',
    new_name='new_field',
),
```

### Deleting a Field

Django automatically detects field removal:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Changing Field Type

```python
# Before: CharField
# After: TextField
field = models.TextField()
```

```bash
python manage.py makemigrations
python manage.py migrate
```

## Migration Management

### Check Migration Status

```bash
python manage.py showmigrations
```

Shows all migrations and their status (applied/unapplied).

### Undo Last Migration

```bash
python manage.py migrate smru 0001
```

This reverts to the specified migration (use migration name/number).

### Reset Database

```bash
# Delete db.sqlite3
rm db.sqlite3

# Re-apply all migrations
python manage.py migrate
```

### Fake Migration

If you've manually changed the database:
```bash
python manage.py migrate --fake smru 0001
```

### Check SQL Before Applying

```bash
python manage.py sqlmigrate smru 0002
```

Shows the SQL that will be executed.

## Best Practices

### 1. Always Create Migrations
```bash
python manage.py makemigrations
```

### 2. Review Generated Code
Check the migration file before applying it.

### 3. Test on Development First
Always test migrations on development before production.

### 4. Descriptive Names
When running with `--name`:
```bash
python manage.py makemigrations --name add_college_website
```

### 5. Commit Migrations to Git
```bash
git add smru/migrations/
git commit -m "Add college website field"
```

### 6. Never Manually Edit Production Data Schema
Always use migrations, not direct SQL.

## Production Migrations

### Before Deploying

1. Create backup:
```bash
pg_dump college_portal > backup.sql
```

2. Test migration:
```bash
python manage.py migrate --plan
```

3. Run migration:
```bash
python manage.py migrate
```

4. Verify:
```bash
python manage.py showmigrations
```

### During Deployment

1. Pull latest code
2. Run migrations:
```bash
python manage.py migrate
```

3. Collect static files:
```bash
python manage.py collectstatic
```

4. Restart application:
```bash
sudo systemctl restart college_portal.service
```

## Troubleshooting

### Migration Conflicts

If you have conflicting migrations:
```
Conflicting migrations detected
```

Resolve by:
1. Merging migrations:
```bash
python manage.py makemigrations --merge
```

2. Edit migration to handle conflict

3. Test thoroughly

### Database Lock

If database is locked:
```bash
# Kill connections
psql -U college_user -d college_portal -c "
  SELECT pg_terminate_backend(pg_stat_activity.pid)
  FROM pg_stat_activity
  WHERE pg_stat_activity.datname = 'college_portal'
  AND pid <> pg_backend_pid();
"
```

### Partial Migration

If migration failed partway:
```bash
python manage.py migrate --fake smru <last_working_migration>
python manage.py migrate
```

## Monitoring Migrations

### View All Migrations
```bash
python manage.py showmigrations smru
```

### Check Specific Migration
```bash
python manage.py sqlmigrate smru 0001
```

### Model Changes
```bash
python manage.py diffsettings
```

## Working with Teams

### Merging Migrations

If multiple developers create migrations:
```bash
python manage.py makemigrations --merge
```

This creates a merge migration.

### Sharing Migrations

Always commit migrations to version control:
```bash
git add smru/migrations/
git commit -m "Add notification expiry feature"
git push
```

## Advanced Topics

### Custom Migrations

Create custom logic:
```bash
python manage.py makemigrations smru --empty --name custom_data_migration
```

Edit the file:
```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('smru', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_function, reverse_function),
    ]

def forward_function(apps, schema_editor):
    College = apps.get_model('smru', 'College')
    # Your custom logic
    pass

def reverse_function(apps, schema_editor):
    # Reverse the operation
    pass
```

### Raw SQL Migrations

```python
migrations.RunSQL(
    "UPDATE smru_college SET is_active=true;",
    reverse_sql="UPDATE smru_college SET is_active=false;",
)
```

## Documentation References

- [Django Migrations](https://docs.djangoproject.com/en/3.2/topics/migrations/)
- [Migration Operations](https://docs.djangoproject.com/en/3.2/ref/migration-operations/)
- [Database API](https://docs.djangoproject.com/en/3.2/topics/db/models/)

---

**Keep migrations clean, documented, and tested!**
