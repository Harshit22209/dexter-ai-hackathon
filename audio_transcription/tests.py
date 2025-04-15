from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import json
from unittest.mock import patch, MagicMock

from .models import AudioFile, Transcription
from .services.transcription_service import TranscriptionService


class AudioTranscriptionModelTests(TestCase):
    """Test cases for audio transcription models"""
    
    def test_audio_file_creation(self):
        """Test creating an AudioFile instance"""
        audio_file = AudioFile.objects.create()
        self.assertFalse(audio_file.processed)
        self.assertIsNotNone(audio_file.uploaded_at)
    
    def test_transcription_creation(self):
        """Test creating a Transcription instance"""
        audio_file = AudioFile.objects.create()
        transcription = Transcription.objects.create(
            audio_file=audio_file,
            json_result={'text': 'Test transcription'}
        )
        self.assertEqual(transcription.audio_file, audio_file)
        self.assertEqual(transcription.json_result['text'], 'Test transcription')


class TranscriptionServiceTests(TestCase):
    """Test cases for the transcription service"""
    
    @patch('audio_transcription.services.transcription_service.whisper')
    @patch('audio_transcription.services.transcription_service.Pipeline')
    @patch('audio_transcription.services.transcription_service.AudioSegment')
    def test_process_audio(self, mock_audio_segment, mock_pipeline, mock_whisper):
        """Test the process_audio method of TranscriptionService"""
        # Mock the whisper model and transcription result
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model
        mock_model.transcribe.return_value = {
            'text': 'This is a test transcription.',
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': 'This is a test'}
            ]
        }
        
        # Mock the diarization pipeline
        mock_diarization = MagicMock()
        mock_pipeline.from_pretrained.return_value = mock_diarization
        mock_diarization.return_value = MagicMock()
        
        # Create a simple mock for AudioSegment
        mock_audio = MagicMock()
        mock_audio_segment.from_file.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio
        mock_audio.set_frame_rate.return_value = mock_audio
        
        # Create an instance of the service and process a file
        service = TranscriptionService(model_size='base')
        
        # Create a temporary file path for testing
        test_file_path = 'test_audio.mp3'
        
        # Process the audio
        with patch('os.path.exists', return_value=True):
            with patch('os.remove'):
                result = service.process_audio(test_file_path)
        
        # Assert expected calls and results
        mock_whisper.load_model.assert_called_once_with('base')
        mock_model.transcribe.assert_called_once()
        
        # Check the result structure
        self.assertIn('text', result)
        self.assertIn('segments', result)
        self.assertEqual(result['text'], 'This is a test transcription.')


class TranscriptionAPIViewTests(TestCase):
    """Test cases for the transcription API views"""
    
    @patch('audio_transcription.views.TranscriptionService')
    def test_transcription_api_view(self, mock_service_class):
        """Test the transcription API view"""
        # Mock the service and its process_audio method
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.process_audio.return_value = {
            'text': 'Test transcription',
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': 'Test', 'speaker': 'SPEAKER_1'}
            ],
            'language': 'en'
        }
        
        # Create a test audio file
        audio_content = b'test audio content'
        test_file = SimpleUploadedFile('test.mp3', audio_content, content_type='audio/mpeg')
        
        # Make a POST request to the transcription API
        url = reverse('transcribe_audio')
        with patch('tempfile.NamedTemporaryFile'):
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    response = self.client.post(url, {'audio': test_file}, format='multipart')
        
        # Assert response is successful
        self.assertEqual(response.status_code, 200)
        
        # Assert service was called correctly
        mock_service_class.assert_called_once()
        mock_service.process_audio.assert_called_once()
        
        # Check response data
        response_data = response.json()
        self.assertIn('text', response_data)
        self.assertIn('segments', response_data)
        self.assertEqual(response_data['text'], 'Test transcription')