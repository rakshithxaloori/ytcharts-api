# Generated by Django 4.2 on 2023-04-28 06:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
