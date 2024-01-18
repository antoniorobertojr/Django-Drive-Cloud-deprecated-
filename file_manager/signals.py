from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import File, Folder, Share


@receiver(post_save, sender=File)
def copy_folder_permissions_to_file(sender, instance, created, **kwargs):
    if created and instance.folder:
        folder_content_type = ContentType.objects.get_for_model(Folder)
        file_content_type = ContentType.objects.get_for_model(File)

        # Copy the permissions from the Folder to the File
        folder_shares = Share.objects.filter(
            content_type=folder_content_type, object_id=instance.folder.id
        )
        for share in folder_shares:
            Share.objects.create(
                shared_by=share.shared_by,
                shared_with=share.shared_with,
                content_type=file_content_type,
                object_id=instance.id,
                can_read=share.can_read,
                can_edit=share.can_edit,
                can_delete=share.can_delete,
                can_share=share.can_share,
            )


@receiver(post_save, sender=Folder)
def copy_parent_folder_permissions_to_subfolder(sender, instance, created, **kwargs):
    if created and instance.parent:
        folder_content_type = ContentType.objects.get_for_model(Folder)

        folder_shares = Share.objects.filter(
            content_type=folder_content_type, object_id=instance.parent.id
        )
        for share in folder_shares:
            Share.objects.create(
                shared_by=share.shared_by,
                shared_with=share.shared_with,
                content_type=folder_content_type,
                object_id=instance.id,
                can_read=share.can_read,
                can_edit=share.can_edit,
                can_delete=share.can_delete,
                can_share=share.can_share,
            )
