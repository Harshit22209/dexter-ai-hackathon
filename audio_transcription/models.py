from django.db import models
from django.utils import timezone
import os
import uuid

def audio_file_path(instance, filename):
    """Generate file path for new audio file"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/audio/', filename)

class AudioFile(models.Model):
    """Model to store audio files for transcription"""
    file = models.FileField(upload_to=audio_file_path)
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Audio file {self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class Transcription(models.Model):
    """Model to store transcription results"""
    audio_file = models.OneToOneField(AudioFile, on_delete=models.CASCADE, related_name='transcription')
    json_result = models.JSONField()
    completed_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Transcription for audio {self.audio_file.id}"