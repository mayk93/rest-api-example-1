from rest_framework import viewsets, mixins, authentication, permissions
from order.serializers import TagSerializer, ItemSerializer
from core.models import Tag, Item


class BaseViewLogic(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class TagViewSet(BaseViewLogic):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class ItemViewSet(BaseViewLogic):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
