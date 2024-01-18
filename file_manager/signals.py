from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import File, Folder, Share


def copy_permissions(
    source_content_type, source_object_id, target_content_type, target_object_id
):
    shares = Share.objects.filter(
        content_type=source_content_type, object_id=source_object_id
    )

    for share in shares:
        Share.objects.create(
            shared_by=share.shared_by,
            shared_with=share.shared_with,
            content_type=target_content_type,
            object_id=target_object_id,
            can_read=share.can_read,
            can_edit=share.can_edit,
            can_delete=share.can_delete,
            can_share=share.can_share,
        )


@receiver(post_save, sender=File)
def copy_folder_permissions_to_file(sender, instance, created, **kwargs):
    if created and instance.folder:
        folder_content_type = ContentType.objects.get_for_model(Folder)
        file_content_type = ContentType.objects.get_for_model(File)

        copy_permissions(
            folder_content_type, instance.folder.id, file_content_type, instance.id
        )


@receiver(post_save, sender=Folder)
def copy_parent_folder_permissions_to_subfolder(sender, instance, created, **kwargs):
    if created and instance.parent:
        folder_content_type = ContentType.objects.get_for_model(Folder)

        copy_permissions(
            folder_content_type, instance.parent.id, folder_content_type, instance.id
        )
