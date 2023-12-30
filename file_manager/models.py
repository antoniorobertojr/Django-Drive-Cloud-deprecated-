from django.conf import settings
from django.db import models
from django.urls import reverse


# TODO get_user() instead of auth user model.
class Folder(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_folders"
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_folders", blank=True
    )
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        full_name = f"{self.name}"
        if self.parent:
            full_name = f"{self.parent}::" + full_name
        return full_name

    @property
    def depth(self):
        if not self.parent:
            return 0
        return self.parent.depth + 1

    def parent_url(self):
        url_list = []
        temp = self
        while temp.parent:
            temp = temp.parent
            url_list.append(reverse("folder:list") + "?id=" + str(temp.pk))

        return url_list


class File(models.Model):
    name = models.CharField(max_length=128)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f'{self.name}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = self.file.name
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @property
    def full_path(self):
        return f'{self.folder}::{self.name}'

    @property
    def extension(self):
        return str(self.name).split('.')[-1]
