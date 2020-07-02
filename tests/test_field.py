import boto3
from botocore.stub import Stubber

from django.test import TestCase
from django.conf import settings

from tests.models import TestModel
from unittest import mock




class FieldTestCase(TestCase):

    @mock.patch('django_kms.fields.get_kms_client')
    def test_save(self, get_client):
        instance = TestModel(
            secure_string="My secure string",
        )

        encrypt_kwargs = {
            'KeyId': settings.KMS_FIELD_KEY,
            'Plaintext': instance.secure_string.encode(),
        }

        encrypt_response = {
            'CiphertextBlob': b'some random string that is pretend encrypted'
        }

        client = boto3.client('kms', 'us-west-2')
        client.encrypt = mock.MagicMock(return_value=encrypt_response)
        # client.encrypt().return_value = encrypt_response

        get_client.return_value = client

        instance.save()

        client.encrypt.assert_called_once_with(**encrypt_kwargs)

        decrypt_kwargs = encrypt_response
        decrypt_response = encrypt_kwargs
        client.decrypt = mock.MagicMock(return_value=decrypt_response)

        instance2 = TestModel.objects.get(pk=instance.pk)

        self.assertEqual(instance2.secure_string, instance.secure_string)
        client.decrypt.assert_called_once_with(**decrypt_kwargs)
