import boto3

from django.db import models
from django.conf import settings
from django.core import checks


def get_kms_client():
    return boto3.client('kms', getattr(settings, 'KMS_FIELD_REGION', 'us-east-1'))


class KMSEncryptedCharField(models.BinaryField):
    def __init__(self, key_id=None, *args, **kwargs):
        kwargs.setdefault('editable', True)
        self.key_id = key_id or getattr(settings, "KMS_FIELD_KEY", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['key_id'] = self.key_id
        return name, path, args, kwargs

    def check(self, **kwargs):
        extra_checks = list()
        if self.key_id is None:
            extra_checks.append(
                checks.Error(
                    "KMSEncryptedCharField must define a key_id attribute or "
                    "settings.KMS_FIELD_KEY must be set.",
                    obj=self,
                )
            )

        return [
            *super().check(**kwargs),
            *extra_checks,
        ]

    @property
    def _kms(self):
        if not hasattr(self, '_kms_client') or settings.UNIT_TEST:
            # Always get_kms_client() in unit tests so mocks work
            client = get_kms_client()
            setattr(self, '_kms_client', client)
        return getattr(self, '_kms_client')

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        result = self._kms.decrypt(CiphertextBlob=value)
        return result.get('Plaintext').decode()

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, str):
            result = self._kms.encrypt(KeyId=self.key_id, Plaintext=value.encode())
            value = super().get_db_prep_value(result['CiphertextBlob'], connection, prepared)
        else:
            value = super().get_db_prep_value(value, connection, prepared)

        if value is not None:
            return connection.Database.Binary(value)
        return value

    def to_python(self, value):
        return value
