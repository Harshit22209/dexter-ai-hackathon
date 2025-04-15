from django.urls import path
from .views import TranscriptionAPIView, TranscriptionDetailAPIView

urlpatterns = [
    path('transcribe/', TranscriptionAPIView.as_view(), name='transcribe_audio'),
    path('transcriptions/', TranscriptionAPIView.as_view(), name='list_transcriptions'),
    path('transcriptions/<int:transcription_id>/', TranscriptionDetailAPIView.as_view(), name='transcription_detail'),
]