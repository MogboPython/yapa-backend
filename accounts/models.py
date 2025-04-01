from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import Model
from eth_typing import ChecksumAddress
from eth_utils.address import is_address, to_checksum_address

from common.models import TimestampedModel, UUIDModel


class EVMAddressField(models.CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs['max_length'] = 42
        super().__init__(*args, **kwargs)

    def validate(self, value: Any, model_instance: Model | None) -> None:
        super().validate(value, model_instance)
        if not is_address(value):
            msg = 'Invalid EVM address provided'
            raise ValidationError(msg)

    def pre_save(self, model_instance: Model, add: bool) -> ChecksumAddress:  # noqa: FBT001
        if add:
            addr = getattr(model_instance, self.attname)
            checksum_addr = to_checksum_address(addr)
            setattr(model_instance, self.attname, checksum_addr)
            return checksum_addr

        return super().pre_save(model_instance, add)


class Account(UUIDModel, TimestampedModel, models.Model):
    address = EVMAddressField('address', unique=True, blank=False)
    username = models.CharField('username', max_length=200, blank=True, default="")
    profile_picture_url = models.URLField(
        'profile_picture_url',
        max_length=500,
        blank=True,
        default="",
        validators=[URLValidator()]
    )

    class Meta:
        db_table = 'accounts'

    # TODO: unnecessary
    def __str__(self):
        return self.address


