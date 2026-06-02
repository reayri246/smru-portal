from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('smru', '0019_remove_whatsapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='whatsapp_number',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
