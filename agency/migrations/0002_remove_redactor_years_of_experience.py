# Generated by Django 4.1.7 on 2023-03-30 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='redactor',
            name='years_of_experience',
        ),
    ]
