from django.db import models

from django_kms import fields


class TestModel(models.Model):
    secure_string = fields.KMSEncryptedStringField()

