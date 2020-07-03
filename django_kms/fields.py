import hashlib

import boto3

from django.db import models
from django.conf import settings
from django.core import checks

from .cache import SimpleCache


def get_kms_client():
    return boto3.client('kms', getattr(settings, 'KMS_FIELD_REGION', 'us-east-1'))


class KMSEncryptedCharField(models.BinaryField):
    def __init__(self, key_id=None, *args, **kwargs):
        kwargs.setdefault('editable', True)
        self.key_id = key_id or getattr(settings, "KMS_FIELD_KEY", None)
        self._ciphertext_cache = SimpleCache(max_size=getattr(settings, "KMS_FIELD_LRU_SIZE", 250))
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
        if not hasattr(self, '_kms_client') or getattr(settings, 'UNIT_TEST', False):
            # Always get_kms_client() in unit tests so mocks work
            client = get_kms_client()
            setattr(self, '_kms_client', client)
        return getattr(self, '_kms_client')

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        ciphertext = bytes(value)
        ciphertext_hash = hashlib.sha1()
        ciphertext_hash.update(ciphertext)
        cache_key = ciphertext_hash.hexdigest()
        try:
            return self._ciphertext_cache.get(cache_key)
        except self._ciphertext_cache.CacheMiss:
            result = self._kms.decrypt(CiphertextBlob=bytes(value))
            new_value = result.get('Plaintext').decode()
            self._ciphertext_cache.set(cache_key, new_value)
            return new_value

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, str):
            result = self._kms.encrypt(KeyId=self.key_id, Plaintext=value.encode())
            return super().get_db_prep_value(result['CiphertextBlob'], connection, prepared)

        return super().get_db_prep_value(value, connection, prepared)

    def to_python(self, value):
        return value
