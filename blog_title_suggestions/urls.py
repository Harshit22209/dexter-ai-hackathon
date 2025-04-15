from django.urls import path
from .views import TitleSuggestionAPIView, BlogPostAPIView, BlogPostDetailAPIView

urlpatterns = [
    path('suggestions/', TitleSuggestionAPIView.as_view(), name='title_suggestions'),
    path('posts/', BlogPostAPIView.as_view(), name='blog_posts'),
    path('posts/<int:post_id>/', BlogPostDetailAPIView.as_view(), name='blog_post_detail'),
]