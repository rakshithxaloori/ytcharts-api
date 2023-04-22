# Generated by Django 4.2 on 2023-04-21 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("emails", "0003_alter_email_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="email",
            name="client",
            field=models.CharField(
                choices=[("r", "Resend"), ("s", "SES")], default="r", max_length=1
            ),
        ),
        migrations.AlterField(
            model_name="emailchartpng",
            name="chart_png",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="c_email_chart_pngs",
                to="emails.chartpng",
            ),
        ),
        migrations.AlterField(
            model_name="emailchartpng",
            name="email",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="e_email_chart_pngs",
                to="emails.email",
            ),
        ),
    ]