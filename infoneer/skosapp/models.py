from __future__ import unicode_literals
from django.db import models
from django.forms import ModelForm


class RdfUpload(models.Model):

    title = models.CharField(max_length=64)
    owner = models.CharField(max_length=64, default='public')
    rdf_file = models.FileField("File", upload_to="rdfs/")
    upload_date = models.DateTimeField(auto_now_add=True)


# FileUpload form class.
class UploadForm(ModelForm):
    class Meta:
        model = RdfUpload
        fields = ['title', 'owner', 'rdf_file', ]
