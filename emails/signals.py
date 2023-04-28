from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.core.files.storage import default_storage


from authentication.models import User
from emails.models import Settings, ChartPNG, EmailChartPNG


# Create a settings instance when a user is created
@receiver(post_save, sender=User)
def create_settings(sender, instance, created, **kwargs):
    if created:
        print("Creating new Settings for User: " + str(instance.username) + " ...")
        message = f"Hi, I'm {instance.first_name} {instance.last_name}, a YouTuber that makes cool vlogs that document my life. I love how your brand caters to everyday life and I've used your products for a few years now. I'd love for us to partner up for a brand deal and have you featured in one of my videos! Check out my monthly views below and take a look at my profile. Let's chat!"
        subject = "Brand Deal"
        Settings.objects.create(
            user=instance, default_message=message, default_subject=subject
        )


# When a ChartPNG is deleted,
# delete the file from S3 using default_storage
@receiver(post_delete, sender=ChartPNG)
def delete_chart_png_from_s3(sender, instance, **kwargs):
    if default_storage.exists(instance.path):
        print("Deleting file from S3: " + instance.path + " ...")
        default_storage.delete(instance.path)


# Create a new EmailChartPNG when a ChartPNG is created
@receiver(post_save, sender=ChartPNG)
def create_email_chart_png(sender, instance, created, **kwargs):
    if created:
        print("Creating new EmailChartPNG for ChartPNG: " + str(instance.id) + " ...")
        EmailChartPNG.objects.create(chart_png=instance)
