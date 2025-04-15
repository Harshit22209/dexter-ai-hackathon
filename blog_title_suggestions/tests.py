from django.test import TestCase
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock

from .models import BlogPost, TitleSuggestion
from .services.title_generator import TitleGenerator


class BlogTitleModelsTests(TestCase):
    """Test cases for blog title suggestion models"""
    
    def test_blog_post_creation(self):
        """Test creating a BlogPost instance"""
        blog_post = BlogPost.objects.create(
            title="Test Blog",
            content="This is a test blog post content."
        )
        self.assertEqual(blog_post.title, "Test Blog")
        self.assertIsNotNone(blog_post.created_at)
        self.assertIsNotNone(blog_post.updated_at)
    
    def test_title_suggestion_creation(self):
        """Test creating a TitleSuggestion instance"""
        blog_post = BlogPost.objects.create(
            title="Test Blog",
            content="This is a test blog post content."
        )
        suggestions = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        title_suggestion = TitleSuggestion.objects.create(
            blog_post=blog_post,
            content="Test content",
            suggestions=suggestions
        )
        self.assertEqual(title_suggestion.blog_post, blog_post)
        self.assertEqual(title_suggestion.suggestions, suggestions)
        self.assertIsNotNone(title_suggestion.created_at)


class TitleGeneratorTests(TestCase):
    """Test cases for the title generator service"""
    
    @patch('blog_title_suggestions.services.title_generator.T5ForConditionalGeneration')
    @patch('blog_title_suggestions.services.title_generator.T5Tokenizer')
    def test_generate_title_suggestions(self, mock_tokenizer_class, mock_model_class):
        """Test the generate_title_suggestions method"""
        # Mock the tokenizer
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_tokenizer.return_value = {'input_ids': MagicMock()}
        mock_tokenizer.decode.side_effect = lambda x, skip_special_tokens: f"Generated Title {x}"
        
        # Mock the model
        mock_model = MagicMock()
        mock_model_class.from_pretrained.return_value = mock_model
        mock_model.generate.return_value = [1, 2, 3]
        
        # Create an instance of the generator and generate titles
        generator = TitleGenerator()
        suggestions = generator.generate_title_suggestions(
            content="This is a test blog post about machine learning.",
            num_suggestions=3
        )
        
        # Assert expected calls
        mock_tokenizer_class.from_pretrained.assert_called_once()
        mock_model_class.from_pretrained.assert_called_once()
        
        # Assert we get the expected number of suggestions
        self.assertEqual(len(suggestions), 3)


class TitleSuggestionAPIViewTests(TestCase):
    """Test cases for the title suggestion API views"""
    
    @patch('blog_title_suggestions.views.TitleGenerator')
    def test_title_suggestion_api_view(self, mock_generator_class):
        """Test the title suggestion API view"""
        # Mock the generator and its generate_title_suggestions method
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_title_suggestions.return_value = [
            "Title Suggestion 1",
            "Title Suggestion 2",
            "Title Suggestion 3"
        ]
        
        # Create test blog content
        test_content = "This is a test blog post content with sufficient length to pass validation."
        
        # Make a POST request to the title suggestion API
        url = reverse('title_suggestions')
        response = self.client.post(
            url, 
            {'content': test_content, 'num_suggestions': 3},
            content_type='application/json'
        )
        
        # Assert response is successful
        self.assertEqual(response.status_code, 200)
        
        # Assert generator was called correctly
        mock_generator_class.assert_called_once()
        mock_generator.generate_title_suggestions.assert_called_once_with(
            content=test_content,
            num_suggestions=3
        )
        
        # Check response data
        response_data = response.json()
        self.assertIn('titles', response_data)
        self.assertEqual(len(response_data['titles']), 3)
        self.assertEqual(response_data['titles'][0], "Title Suggestion 1")


class BlogPostAPIViewTests(TestCase):
    """Test cases for the blog post API views"""
    
    def test_create_blog_post(self):
        """Test creating a blog post"""
        # Create test data
        test_data = {
            'title': 'Test Blog Post',
            'content': 'This is the content of the test blog post.'
        }
        
        # Make a POST request to create a blog post
        url = reverse('blog_posts')
        response = self.client.post(
            url,
            test_data,
            content_type='application/json'
        )
        
        # Assert response is successful
        self.assertEqual(response.status_code, 201)
        
        # Check response data
        response_data = response.json()
        self.assertIn('id', response_data)
        self.assertEqual(response_data['title'], test_data['title'])
        
        # Check that the blog post was created in the database
        blog_post = BlogPost.objects.get(id=response_data['id'])
        self.assertEqual(blog_post.title, test_data['title'])
        self.assertEqual(blog_post.content, test_data['content'])
    
    @patch('blog_title_suggestions.views.TitleGenerator')
    def test_create_blog_post_with_suggestions(self, mock_generator_class):
        """Test creating a blog post with title suggestions"""
        # Mock the generator and its generate_title_suggestions method
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_title_suggestions.return_value = [
            "Title Suggestion 1",
            "Title Suggestion 2",
            "Title Suggestion 3"
        ]
        
        # Create test data
        test_data = {
            'title': 'Test Blog Post',
            'content': 'This is the content of the test blog post.',
            'generate_suggestions': True
        }
        
        # Make a POST request to create a blog post with suggestions
        url = reverse('blog_posts')
        response = self.client.post(
            url,
            test_data,
            content_type='application/json'
        )
        
        # Assert response is successful
        self.assertEqual(response.status_code, 201)
        
        # Check response data
        response_data = response.json()
        self.assertIn('id', response_data)
        self.assertEqual(response_data['title'], test_data['title'])
        self.assertIn('title_suggestions', response_data)
        self.assertEqual(len(response_data['title_suggestions']), 3)