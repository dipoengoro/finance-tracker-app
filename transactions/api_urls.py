from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'transactions', api_views.TransactionViewSet, basename='transaction')
router.register(r'categories', api_views.CategoryListCreateAPIView, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]