import os
import json
import tempfile
import torch
import whisper
from pyannote.audio import Pipeline
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for handling audio transcription with speaker diarization"""
    
    def __init__(self, model_size="base"):
        """Initialize the service with specified whisper model size"""
        self.model_size = model_size
        self.whisper_model = None
        self.diarization_pipeline = None
        
    def _load_models(self):
        """Load the required models (lazy loading to save resources)"""
        if self.whisper_model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.whisper_model = whisper.load_model(self.model_size)
        
        if self.diarization_pipeline is None:
            logger.info("Loading diarization pipeline")
            # In a production environment, you would need proper authentication
            # with HuggingFace to use pyannote.audio
            try:
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.0",
                    use_auth_token=os.getenv('HUGGINGFACE_TOKEN')
                )
            except Exception as e:
                logger.error(f"Error loading diarization model: {e}")
                # Fall back to a simple time-based diarization as fallback
                self.diarization_pipeline = None
    
    def _convert_audio_format(self, audio_path, output_path=None):
        """Convert audio to appropriate format for processing"""
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.wav')
        
        # Convert to WAV format with appropriate parameters for diarization
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)  # Mono
        audio = audio.set_frame_rate(16000)  # 16kHz
        audio.export(output_path, format='wav')
        
        return output_path
    
    def _perform_diarization(self, audio_path):
        """Perform speaker diarization on the audio file"""
        try:
            if self.diarization_pipeline is None:
                # Simplified diarization for demo purposes
                return self._simple_diarization(audio_path)
            
            # Real diarization with pyannote
            diarization = self.diarization_pipeline(audio_path)
            
            # Convert diarization result to a list of segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': speaker
                })
            
            return segments
        except Exception as e:
            logger.error(f"Diarization error: {e}")
            # Fallback to simple diarization
            return self._simple_diarization(audio_path)
    
    def _simple_diarization(self, audio_path):
        """Simple time-based diarization as fallback"""
        # This is a very simplified approach - in production you'd want proper diarization
        audio = AudioSegment.from_file(audio_path)
        duration_seconds = len(audio) / 1000
        
        # Roughly divide the audio into segments, alternating between speakers
        segment_length = 10  # seconds per segment
        segments = []
        
        for i in range(0, int(duration_seconds), segment_length):
            speaker = f"SPEAKER_{1 if i % 20 < 10 else 2}"
            end = min(i + segment_length, duration_seconds)
            segments.append({
                'start': i,
                'end': end,
                'speaker': speaker
            })
        
        return segments
    
    def _transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper"""
        try:
            result = self.whisper_model.transcribe(audio_path)
            return result
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    def _merge_transcription_with_diarization(self, transcription, diarization):
        """Merge transcription with diarization information"""
        merged_segments = []
        
        for segment in transcription['segments']:
            # Find the speaker for this segment
            start_time = segment['start']
            end_time = segment['end']
            
            # Find overlapping diarization segments
            overlapping_speakers = []
            for diar_segment in diarization:
                if (diar_segment['end'] > start_time and 
                    diar_segment['start'] < end_time):
                    overlapping_speakers.append(diar_segment['speaker'])
            
            # Use the most common speaker or "UNKNOWN" if none found
            speaker = max(set(overlapping_speakers), key=overlapping_speakers.count) if overlapping_speakers else "UNKNOWN"
            
            merged_segments.append({
                'start': start_time,
                'end': end_time,
                'text': segment['text'].strip(),
                'speaker': speaker
            })
        
        return {
            'segments': merged_segments,
            'text': transcription['text'],
            'language': transcription.get('language', 'en')
        }
    
    def process_audio(self, audio_file_path):
        """Process audio file for transcription with diarization"""
        # Load models if not already loaded
        self._load_models()
        
        # Convert audio to appropriate format
        processed_audio_path = self._convert_audio_format(audio_file_path)
        
        try:
            # Perform transcription
            transcription = self._transcribe_audio(processed_audio_path)
            
            # Perform diarization
            diarization = self._perform_diarization(processed_audio_path)
            
            # Merge results
            result = self._merge_transcription_with_diarization(transcription, diarization)
            
            # Clean up
            if os.path.exists(processed_audio_path) and processed_audio_path != audio_file_path:
                os.remove(processed_audio_path)
            
            return result
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            # Clean up on error
            if os.path.exists(processed_audio_path) and processed_audio_path != audio_file_path:
                os.remove(processed_audio_path)
            raise