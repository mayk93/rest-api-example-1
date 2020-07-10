from core.models import Order, Item, Tag


def sample_order(user, **params):
    defaults = {
        'notes': 'Order notes',
        'delivery_time': 5,
        'price': 10.0,
        'link': 'link to order'
    }
    defaults.update(params)

    return Order.objects.create(user=user, **defaults)


def sample_item(user, **params):
    defaults = {
        'name': 'Item'
    }
    defaults.update(params)

    return Item.objects.create(user=user, **defaults)


def sample_tag(user, **params):
    defaults = {
        'name': 'Tag'
    }
    defaults.update(params)

    return Tag.objects.create(user=user, **defaults)
