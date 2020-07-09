from core.models import Order


def sample_order(user, **params):
    defaults = {
        'notes': 'Order notes',
        'delivery_time': 5,
        'price': 10.0,
        'link': 'link to order'
    }
    defaults.update(params)

    return Order.objects.create(user=user, **defaults)
