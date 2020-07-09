from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


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

    def __str__(self):
        return f'Order ID: {self.id}'
