from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
import os
import tempfile
import logging

from .models import AudioFile, Transcription
from .services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)

class TranscriptionAPIView(APIView):
    """
    API endpoint for audio transcription with diarization
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """
        Process an audio file and return transcription with diarization
        """
        # Check if audio file is provided
        if 'audio' not in request.FILES:
            return Response(
                {"error": "No audio file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio']
        
        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, dir=settings.TEMP_DIR, suffix=os.path.splitext(audio_file.name)[1]) as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Get model size from request or use default
            model_size = request.data.get('model_size', 'base')
            
            # Initialize the transcription service with specified model size
            transcription_service = TranscriptionService(model_size=model_size)
            
            # Process the audio file
            result = transcription_service.process_audio(temp_file_path)
            
            # Save to database (optional, for keeping track of processed files)
            audio_model = AudioFile.objects.create(
                file=audio_file,
                processed=True
            )
            
            transcription = Transcription.objects.create(
                audio_file=audio_model,
                json_result=result,
                completed_at=timezone.now()
            )
            
            # Remove the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            # Format the response for the API
            response_data = {
                'transcription_id': transcription.id,
                'text': result['text'],
                'segments': result['segments'],
                'language': result.get('language', 'en'),
                'processed_at': transcription.completed_at.isoformat()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in transcription process: {str(e)}")
            
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return Response(
                {"error": f"Transcription failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def get(self, request, *args, **kwargs):
        """
        Get a list of previous transcriptions
        """
        transcriptions = Transcription.objects.all().order_by('-completed_at')[:10]
        
        response_data = [{
            'id': t.id,
            'audio_file_id': t.audio_file.id,
            'completed_at': t.completed_at.isoformat(),
            'text': t.json_result.get('text', '')[:100] + '...' if len(t.json_result.get('text', '')) > 100 else t.json_result.get('text', '')
        } for t in transcriptions]
        
        return Response(response_data, status=status.HTTP_200_OK)


class TranscriptionDetailAPIView(APIView):
    """
    API endpoint to get a specific transcription result
    """
    def get(self, request, transcription_id, *args, **kwargs):
        """
        Get a specific transcription by ID
        """
        try:
            transcription = Transcription.objects.get(id=transcription_id)
            
            response_data = {
                'transcription_id': transcription.id,
                'text': transcription.json_result.get('text', ''),
                'segments': transcription.json_result.get('segments', []),
                'language': transcription.json_result.get('language', 'en'),
                'processed_at': transcription.completed_at.isoformat()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Transcription.DoesNotExist:
            return Response(
                {"error": "Transcription not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving transcription: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve transcription: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )