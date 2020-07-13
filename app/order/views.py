from rest_framework import \
    viewsets, mixins, status, authentication, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from order.serializers import \
    TagSerializer, ItemSerializer,\
    OrderSerializer, OrderDetailSerializer, OrderImageSerializer
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
    inheritance_list=(viewsets.ModelViewSet,)
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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'upload_image':
            return OrderImageSerializer
        return OrderSerializer

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(
            order,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
