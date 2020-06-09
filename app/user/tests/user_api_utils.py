from django.contrib.auth import get_user_model


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def get_user(**params):
    return get_user_model().objects.get(**params)


def get_user_exists(email):
    return get_user_model().objects.filter(email=email).exists()
