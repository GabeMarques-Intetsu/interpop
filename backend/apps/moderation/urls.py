from django.urls import path
from .views import BanDestroyView, BanListCreateView

urlpatterns = [
    path('moderation/bans/',          BanListCreateView.as_view(), name='ban-list'),
    path('moderation/bans/<uuid:pk>/', BanDestroyView.as_view(),   name='ban-detail'),
]
