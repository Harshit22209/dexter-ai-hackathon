from django.core.management.base import BaseCommand, CommandError
from blog_title_suggestions.services.title_generator import TitleGenerator
import sys
import json


class Command(BaseCommand):
    help = 'Generate title suggestions for blog content'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to a text file containing blog content')
        parser.add_argument('--content', type=str, help='Blog content directly from command line')
        parser.add_argument('--num', type=int, default=3, help='Number of suggestions to generate')
        parser.add_argument('--output', type=str, help='Output file path for JSON result')

    def handle(self, *args, **options):
        file_path = options.get('file')
        content = options.get('content')
        num_suggestions = options.get('num', 3)
        output_file = options.get('output')

        # Get content either from file or command line
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except Exception as e:
                raise CommandError(f'Error reading file: {e}')
        
        if not content:
            raise CommandError('Please provide content either via --file or --content')

        # Initialize the title generator
        self.stdout.write('Generating title suggestions...')
        
        title_generator = TitleGenerator()
        try:
            suggestions = title_generator.generate_title_suggestions(
                content=content,
                num_suggestions=num_suggestions
            )
        except Exception as e:
            raise CommandError(f'Error generating suggestions: {e}')

        # Output results
        result = {
            'titles': suggestions,
            'content_preview': content[:100] + '...' if len(content) > 100 else content
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                self.stdout.write(self.style.SUCCESS(f'Saved suggestions to {output_file}'))
            except Exception as e:
                raise CommandError(f'Error writing to output file: {e}')
        else:
            self.stdout.write(self.style.SUCCESS('Generated title suggestions:'))
            for i, title in enumerate(suggestions, 1):
                self.stdout.write(f'{i}. {title}')