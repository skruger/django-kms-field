# django-kms-field
[![Build Status](https://travis-ci.org/skruger/django-kms-field.svg?branch=master)](https://travis-ci.org/skruger/django-kms-field)

KMS encrypted database field for Django.

The KMSEncryptedCharField uses your KMS key to encrypt your
data before it is stored in the database and it decrypts it again
when you read from the database.

It was designed with stored credentials and other critical
private data in mind. I would strongly recommend thinking
about which models use this field with as it has not been
optomized for high volume access and boto api calls
during query time may impact performance. Splitting secure
fields into separate models can improve performance
significantly as opposed to putting encrypted fields in
frequently read and saved models.

### Example
```python
from django.db import models
from django_kms.fields import KMSEncryptedCharField


class StoredCredential(models.Model):
    description = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = KMSEncryptedCharField(key_id="alias/my_key")

```

### Django settings
```python
KMS_FIELD_KEY = 'alias/<my-key>'
KMS_FIELD_REGION = 'us-west-2'
KMS_FIELD_CACHE_SIZE = 500  # Number of decrypted plaintext values to hold in memory
```
