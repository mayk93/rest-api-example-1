import os
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def order_image_file_name(_, filename):
    extension = filename.split('.')[-1]
    new_name = f'{uuid.uuid4()}.{extension}'
    return os.path.join(settings.BASE_UPLOAD_PATH, new_name)


def validate_regular_increment(value, increment=5):
    if value % increment != 0:
        raise ValidationError(
            f'Value {value} is not a regular increment of ${increment}'
        )


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    notes = models.CharField(max_length=255)
    delivery_time = models.PositiveIntegerField(
        validators=[validate_regular_increment]
    )
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    items = models.ManyToManyField('Item')
    tags = models.ManyToManyField('Tag')

    image = models.ImageField(null=True, upload_to=order_image_file_name)

    def __str__(self):
        return f'Order ID: {self.id}'
