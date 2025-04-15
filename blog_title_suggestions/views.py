from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging

from .models import BlogPost, TitleSuggestion
from .services.title_generator import TitleGenerator

logger = logging.getLogger(__name__)

class TitleSuggestionAPIView(APIView):
    """
    API endpoint for generating blog post title suggestions
    """
    def post(self, request, *args, **kwargs):
        """
        Generate title suggestions based on blog post content
        """
        # Get content from request
        content = request.data.get('content')
        
        if not content or len(content.strip()) < 50:
            return Response(
                {"error": "Please provide blog content with at least 50 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get number of suggestions from request or use default
            num_suggestions = int(request.data.get('num_suggestions', 3))
            num_suggestions = min(max(num_suggestions, 1), 5)  # Limit between 1 and 5
            
            # Initialize the title generator
            title_generator = TitleGenerator()
            
            # Generate title suggestions
            suggestions = title_generator.generate_title_suggestions(
                content=content,
                num_suggestions=num_suggestions
            )
            
            # Save to database (optional)
            title_suggestion = TitleSuggestion.objects.create(
                content=content[:1000],  # Store a preview of the content
                suggestions=suggestions
            )
            
            # Return suggestions
            response_data = {
                'suggestion_id': title_suggestion.id,
                'titles': suggestions
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating title suggestions: {str(e)}")
            return Response(
                {"error": f"Failed to generate title suggestions: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, *args, **kwargs):
        """
        Get a list of previous title suggestions
        """
        suggestions = TitleSuggestion.objects.all().order_by('-created_at')[:10]
        
        response_data = [{
            'id': s.id,
            'titles': s.suggestions,
            'created_at': s.created_at.isoformat(),
            'content_preview': s.content[:100] + '...' if len(s.content) > 100 else s.content
        } for s in suggestions]
        
        return Response(response_data, status=status.HTTP_200_OK)


class BlogPostAPIView(APIView):
    """
    API endpoint for blog posts
    """
    def post(self, request, *args, **kwargs):
        """
        Create a new blog post with optional title suggestions
        """
        title = request.data.get('title')
        content = request.data.get('content')
        
        if not title or not content:
            return Response(
                {"error": "Both title and content are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create blog post
            blog_post = BlogPost.objects.create(
                title=title,
                content=content
            )
            
            # Generate title suggestions
            generate_suggestions = request.data.get('generate_suggestions', False)
            suggestions = []
            
            if generate_suggestions:
                title_generator = TitleGenerator()
                suggestions = title_generator.generate_title_suggestions(content=content)
                
                # Save suggestions
                TitleSuggestion.objects.create(
                    blog_post=blog_post,
                    content=content[:1000],
                    suggestions=suggestions
                )
            
            # Return response
            response_data = {
                'id': blog_post.id,
                'title': blog_post.title,
                'content_preview': blog_post.content[:200] + '...' if len(blog_post.content) > 200 else blog_post.content,
                'created_at': blog_post.created_at.isoformat()
            }
            
            if generate_suggestions:
                response_data['title_suggestions'] = suggestions
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating blog post: {str(e)}")
            return Response(
                {"error": f"Failed to create blog post: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, *args, **kwargs):
        """
        Get a list of blog posts
        """
        blog_posts = BlogPost.objects.all().order_by('-created_at')[:10]
        
        response_data = [{
            'id': post.id,
            'title': post.title,
            'content_preview': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'created_at': post.created_at.isoformat()
        } for post in blog_posts]
        
        return Response(response_data, status=status.HTTP_200_OK)


class BlogPostDetailAPIView(APIView):
    """
    API endpoint for specific blog post
    """
    def get(self, request, post_id, *args, **kwargs):
        """
        Get a specific blog post by ID
        """
        blog_post = get_object_or_404(BlogPost, id=post_id)
        
        # Get title suggestions if they exist
        try:
            title_suggestions = TitleSuggestion.objects.filter(blog_post=blog_post).first()
            suggestions = title_suggestions.suggestions if title_suggestions else []
        except Exception:
            suggestions = []
        
        response_data = {
            'id': blog_post.id,
            'title': blog_post.title,
            'content': blog_post.content,
            'created_at': blog_post.created_at.isoformat(),
            'updated_at': blog_post.updated_at.isoformat(),
            'title_suggestions': suggestions
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def put(self, request, post_id, *args, **kwargs):
        """
        Update a blog post and optionally generate new title suggestions
        """
        blog_post = get_object_or_404(BlogPost, id=post_id)
        
        title = request.data.get('title')
        content = request.data.get('content')
        
        if title:
            blog_post.title = title
        
        if content:
            blog_post.content = content
        
        blog_post.save()
        
        # Generate new title suggestions if requested
        generate_suggestions = request.data.get('generate_suggestions', False)
        suggestions = []
        
        if generate_suggestions and content:
            title_generator = TitleGenerator()
            suggestions = title_generator.generate_title_suggestions(content=content)
            
            # Save new suggestions
            TitleSuggestion.objects.create(
                blog_post=blog_post,
                content=content[:1000],
                suggestions=suggestions
            )
        
        # Return response
        response_data = {
            'id': blog_post.id,
            'title': blog_post.title,
            'content_preview': blog_post.content[:200] + '...' if len(blog_post.content) > 200 else blog_post.content,
            'updated_at': blog_post.updated_at.isoformat()
        }
        
        if generate_suggestions:
            response_data['title_suggestions'] = suggestions
        
        return Response(response_data, status=status.HTTP_200_OK)