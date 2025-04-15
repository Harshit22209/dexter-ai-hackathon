from django.contrib import admin
from .models import AudioFile, Transcription

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'processed')
    list_filter = ('processed',)
    search_fields = ('id',)
    readonly_fields = ('uploaded_at',)

@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'audio_file', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('id', 'audio_file__id')
    readonly_fields = ('completed_at',)