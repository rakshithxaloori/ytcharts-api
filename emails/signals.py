from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.files.storage import default_storage


from emails.models import ChartPNG


# When a ChartPNG is deleted,
# delete the file from S3 using default_storage
@receiver(post_delete, sender=ChartPNG)
def delete_chart_png_from_s3(sender, instance, **kwargs):
    if default_storage.exists(instance.path):
        print("Deleting file from S3: " + instance.path + " ...")
        default_storage.delete(instance.path)
