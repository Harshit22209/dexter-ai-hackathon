from django.db import models
from django.utils import timezone

class BlogPost(models.Model):
    """Model to represent blog posts"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class TitleSuggestion(models.Model):
    """Model to store title suggestions for blog posts"""
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='title_suggestions', null=True, blank=True)
    content = models.TextField()  # The content used to generate suggestions
    suggestions = models.JSONField()  # List of suggested titles
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Title suggestions for {self.blog_post.title if self.blog_post else 'draft content'}"