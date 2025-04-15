from django.contrib import admin
from .models import BlogPost, TitleSuggestion

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(TitleSuggestion)
class TitleSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog_post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'blog_post__title')
    readonly_fields = ('created_at',)
    
    def get_suggestions(self, obj):
        """Display the suggestions in a readable format"""
        if obj.suggestions:
            return "\n".join([f"- {suggestion}" for suggestion in obj.suggestions])
        return "No suggestions"
    
    get_suggestions.short_description = 'Title Suggestions'