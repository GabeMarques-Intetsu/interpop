from django.urls import path, register_converter

from apps.articles.converters import UnicodeSlugConverter
from .views import CommentDestroyView, CommentListCreateView, CommentLikeToggleView

# Same unicode-aware slug converter as the articles app — required so that
# article slugs containing accented characters (à, ç, é, …) resolve here too.
register_converter(UnicodeSlugConverter, 'uslug')

urlpatterns = [
    path('articles/<uslug:slug>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<uuid:pk>/',             CommentDestroyView.as_view(),    name='comment-delete'),
    path('comments/<uuid:pk>/like/',        CommentLikeToggleView.as_view(), name='comment-like'),
]
