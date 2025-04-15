# Darwix AI Project

A Django-based application implementing two AI features:
1. Audio Transcription with Speaker Diarization
2. AI-powered Blog Post Title Suggestions

## Features

### Audio Transcription with Diarization
- Transcribes audio files into text
- Identifies different speakers in the audio (diarization)
- Supports various audio formats (MP3, WAV, etc.)
- Returns structured JSON with timestamps and speaker identification
- Supports multilingual audio transcription

### Blog Post Title Suggestions
- Analyzes blog post content using NLP
- Generates relevant title suggestions
- Returns multiple options for titles
- Integrated with a Django blog application
- Customizable number of suggestions

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Audio Processing**: OpenAI Whisper, PyAnnote Audio, PyDub
- **NLP**: Transformers (T5), PyTorch
- **API Documentation**: Swagger/OpenAPI via drf-yasg
- **Data Storage**: SQLite (for demo purposes)

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)
- ffmpeg (required for audio processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/darwix-ai-project.git
cd darwix-ai-project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install ffmpeg (if not already installed):
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

5. Create a .env file with your configuration:
```bash
cp .env.example .env
```

6. Edit the .env file with your settings (especially the HuggingFace token):
```
SECRET_KEY=your_django_secret_key_here
DEBUG=True
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

7. Set up the database:
```bash
python manage.py makemigrations audio_transcription
python manage.py makemigrations blog_title_suggestions
python manage.py migrate
```

8. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

9. Run the development server:
```bash
python manage.py runserver
```

The application should now be accessible at `http://localhost:8000/`.

## Code Structure

```
darwix_ai_project/
├── audio_transcription/     # Audio transcription app
│   ├── models.py            # Database models for audio files
│   ├── services/            # Business logic
│   │   └── transcription_service.py  # Audio processing service
│   ├── views.py             # API endpoints
│   └── urls.py              # URL routing
├── blog_title_suggestions/  # Blog title suggestions app
│   ├── models.py            # Database models for blog posts
│   ├── services/            # Business logic
│   │   └── title_generator.py  # NLP-based title generator
│   ├── views.py             # API endpoints
│   └── urls.py              # URL routing
├── darwix_ai_project/       # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI config
├── test_api.py              # Script for testing APIs
├── manage.py                # Django management script
└── requirements.txt         # Project dependencies
```

## API Endpoints

### API Documentation
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

### Audio Transcription with Diarization

#### Transcribe Audio
- **URL**: `/api/audio/transcribe/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `audio`: Audio file to transcribe (required)
  - `model_size`: Whisper model size (optional, default: 'base')
- **Response**: JSON with transcription results including speaker diarization

Example cURL request:
```bash
curl -X POST -F "audio=@test_data/audio_samples/conversation.mp3" http://localhost:8000/api/audio/transcribe/
```

Example response:
```json
{
  "transcription_id": 1,
  "text": "Full transcription text goes here.",
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Hello, my name is Speaker 1.",
      "speaker": "SPEAKER_1"
    },
    {
      "start": 5.5,
      "end": 10.3,
      "text": "And I'm Speaker 2. Nice to meet you.",
      "speaker": "SPEAKER_2"
    }
  ],
  "language": "en",
  "processed_at": "2023-11-15T10:30:45.123456Z"
}
```

#### List Transcriptions
- **URL**: `/api/audio/transcriptions/`
- **Method**: `GET`
- **Response**: List of previous transcriptions

#### Get Transcription Detail
- **URL**: `/api/audio/transcriptions/{transcription_id}/`
- **Method**: `GET`
- **Response**: Detailed transcription result

### Blog Post Title Suggestions

#### Generate Title Suggestions
- **URL**: `/api/blog/suggestions/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "content": "Your blog post content goes here. This should be at least a paragraph to get good suggestions.",
    "num_suggestions": 3
  }
  ```
- **Response**: JSON with title suggestions

Example cURL request:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"content": "Machine learning has transformed the way we approach problem-solving. From predictive analytics to natural language processing, ML algorithms continue to revolutionize industries worldwide...", "num_suggestions": 3}' http://localhost:8000/api/blog/suggestions/
```

Example response:
```json
{
  "suggestion_id": 1,
  "titles": [
    "The Revolutionary Impact of Machine Learning on Problem-Solving",
    "How Machine Learning is Transforming Industries Worldwide",
    "Machine Learning: A New Paradigm in Predictive Analytics"
  ]
}
```

#### Create Blog Post
- **URL**: `/api/blog/posts/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "title": "Your Blog Title",
    "content": "Your blog post content",
    "generate_suggestions": true
  }
  ```
- **Response**: Created blog post with optional title suggestions

## Testing Instructions

### Prepare Test Data

1. Create directories for test data:
```bash
mkdir -p test_data/audio_samples
mkdir -p test_data/blog_samples
```

2. Add test audio files to `test_data/audio_samples/`
3. Create sample blog content files in `test_data/blog_samples/`:
```bash
cat > test_data/blog_samples/ai_article.txt << 'EOF'
Artificial Intelligence: Current Applications and Future Implications

Recent advancements in artificial intelligence have dramatically transformed multiple industries. From healthcare to finance, AI algorithms are automating processes, enhancing decision-making, and creating new possibilities previously thought impossible.

In healthcare, machine learning models now detect diseases from medical images with accuracy rivaling trained radiologists. Natural language processing algorithms analyze patient records to identify patterns and risk factors that might be missed by human practitioners.
EOF
```

### Using the Test Script

The included `test_api.py` script allows easy testing of the API endpoints:

#### Test Audio Transcription
```bash
python test_api.py --audio test_data/audio_samples/conversation.mp3
```

#### Test Blog Title Suggestions
```bash
python test_api.py --blog test_data/blog_samples/ai_article.txt
```

#### Run All Tests
```bash
python test_api.py --all
```

### Using Management Commands

The project includes custom Django management commands for direct testing without using HTTP requests:

#### Test Audio Transcription
```bash
python manage.py transcribe_audio test_data/audio_samples/conversation.mp3 --model base
```

#### Test Title Generation
```bash
python manage.py generate_titles --file test_data/blog_samples/ai_article.txt
```

#### Generate Titles from Command Line
```bash
python manage.py generate_titles --content "Artificial intelligence is rapidly transforming healthcare delivery and patient outcomes. Recent advancements in deep learning algorithms now allow for earlier detection of diseases."
```

## Troubleshooting

### Common Issues

1. **Missing ffmpeg**
   - Error: `Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work`
   - Solution: Install ffmpeg using your system's package manager

2. **Database Errors**
   - Error: `no such table: blog_title_suggestions_titlesuggestion`
   - Solution: Ensure migrations are applied:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

3. **Port Already in Use**
   - Error: `Error: That port is already in use.`
   - Solution: Use a different port:
     ```bash
     python manage.py runserver 8001
     ```
   - Or find and kill the process using port 8000:
     ```bash
     sudo lsof -i :8000
     kill -9 [PID]
     ```

4. **HuggingFace Token Issues**
   - Error: `Error loading diarization model`
   - Solution: Get a valid HuggingFace token and add it to your `.env` file

### Checking Logs

If you're experiencing issues, check the log files:
```bash
mkdir -p logs  # Create logs directory if it doesn't exist
touch logs/django.log  # Create log file if it doesn't exist
tail -f logs/django.log
```

## Performance Considerations

- Audio transcription can be resource-intensive, especially for larger files
- The first run will download AI models, which may take time
- T5 model for title generation requires substantial memory

## Future Improvements

- Add user authentication and permission controls
- Implement a job queue for audio processing with Celery
- Improve the NLP model with fine-tuning on domain-specific data
- Add frontend components for better user experience
- Implement more sophisticated diarization with speaker identification

## License

MIT

## Contact

For any questions or support, please contact [your-email@example.com](mailto:your-email@example.com).
