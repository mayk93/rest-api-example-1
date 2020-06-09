from django.urls import path, include
from rest_framework.routers import DefaultRouter
from order import views

app_name = 'order'

router = DefaultRouter()
router.register('tags', views.TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
