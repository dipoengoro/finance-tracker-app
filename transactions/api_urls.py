from django.urls import path
from . import api_views

urlpatterns = [
    path('categories/', api_views.CategoryListCreateAPIView.as_view(), name='api-category-list'),
]