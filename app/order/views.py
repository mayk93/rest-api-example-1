from rest_framework import viewsets, mixins, authentication, permissions
from order.serializers import TagSerializer, ItemSerializer, OrderSerializer
from core.models import Order, Item, Tag

DEFAULT_INHERITANCE_LIST = (
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
)


def base_view_logic_builder(
        inheritance_list=DEFAULT_INHERITANCE_LIST,
        **kwargs
):
    class _BaseViewLogic(*inheritance_list):
        authentication_classes = (authentication.TokenAuthentication,)
        permission_classes = (permissions.IsAuthenticated,)

        def get_queryset(self):
            return self.queryset \
                .filter(user=self.request.user) \
                .order_by(f'-{kwargs.get("order_by", "id")}')

        def perform_create(self, serializer):
            serializer.save(
                user=self.request.user
            )

    return _BaseViewLogic


BaseViewLogic = base_view_logic_builder(
    order_by='name'
)
BaseModelViewSet = base_view_logic_builder(
    inheritence_list=(viewsets.ModelViewSet,)
)


class TagViewSet(BaseViewLogic):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class ItemViewSet(BaseViewLogic):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class OrderViewSet(BaseModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
