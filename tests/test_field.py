import boto3
from botocore.stub import Stubber

from django.test import TestCase
from django.conf import settings
from django import forms

from tests.models import TestModel
from unittest import mock


class TestForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = (
            'secure_string',
        )


class FieldTestCase(TestCase):

    @mock.patch('django_kms.fields.get_kms_client')
    def test_model_save(self, get_client):
        instance = TestModel(
            secure_string="My model save secure string",
        )

        encrypt_kwargs = {
            'KeyId': settings.KMS_FIELD_KEY,
            'Plaintext': instance.secure_string.encode(),
        }

        encrypt_response = {
            'CiphertextBlob': b'some random string that is pretend encrypted'
        }

        client = boto3.client('kms', 'us-west-2')
        client.encrypt = mock.Mock()
        client.encrypt = mock.MagicMock(return_value=encrypt_response)

        get_client.return_value = client

        instance.save()

        client.encrypt.assert_called_once_with(**encrypt_kwargs)

        decrypt_kwargs = encrypt_response
        decrypt_response = encrypt_kwargs
        client.decrypt = mock.MagicMock(return_value=decrypt_response)

        instance2 = TestModel.objects.get(pk=instance.pk)

        self.assertEqual(instance2.secure_string, instance.secure_string)
        client.decrypt.assert_called_once_with(**decrypt_kwargs)

        instance3 = TestModel.objects.get(pk=instance.pk)

        self.assertEqual(instance3.secure_string, instance.secure_string)
        client.decrypt.assert_called_once_with(**decrypt_kwargs)

    @mock.patch('django_kms.fields.get_kms_client')
    def test_form_save(self, get_client):
        test_string = "This is the form value to be encrypted"

        encrypt_kwargs = {
            'KeyId': settings.KMS_FIELD_KEY,
            'Plaintext': test_string.encode(),
        }

        encrypt_response = {
            'CiphertextBlob': b'Pretend encrypted'
        }

        client = boto3.client('kms', 'us-west-2')
        client.encrypt = mock.MagicMock(return_value=encrypt_response)

        get_client.return_value = client

        form = TestForm({'secure_string': test_string})
        form.full_clean()

        instance = form.save(commit=False)
        self.assertEqual(instance.secure_string, test_string)

        instance.save()

        client.encrypt.assert_called_once_with(**encrypt_kwargs)

        decrypt_kwargs = encrypt_response
        decrypt_response = encrypt_kwargs
        client.decrypt = mock.MagicMock(return_value=decrypt_response)

        instance2 = TestModel.objects.get(pk=instance.pk)

        self.assertEqual(instance2.secure_string, instance.secure_string)
        client.decrypt.assert_called_once_with(**decrypt_kwargs)
