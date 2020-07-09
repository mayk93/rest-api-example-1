from rest_framework import serializers
from core.models import Order
from core.models import Tag
from core.models import Item


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Item.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'items',
            'tags',
            'notes',
            'delivery_time',
            'price',
            'link'
        )
        read_only_fields = ('id',)
