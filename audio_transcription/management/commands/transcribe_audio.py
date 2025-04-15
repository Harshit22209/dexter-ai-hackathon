from django.core.management.base import BaseCommand, CommandError
from audio_transcription.services.transcription_service import TranscriptionService
import json


class Command(BaseCommand):
    help = 'Transcribe an audio file with speaker diarization'

    def add_arguments(self, parser):
        parser.add_argument('audio_file', type=str, help='Path to the audio file to transcribe')
        parser.add_argument('--model', type=str, default='base', 
                            choices=['tiny', 'base', 'small', 'medium', 'large'],
                            help='Whisper model size to use')
        parser.add_argument('--output', type=str, help='Output file path for JSON result')

    def handle(self, *args, **options):
        audio_file = options['audio_file']
        model_size = options['model']
        output_file = options.get('output')

        self.stdout.write(f'Transcribing audio file: {audio_file}')
        self.stdout.write(f'Using Whisper model: {model_size}')
        
        # Initialize the transcription service
        transcription_service = TranscriptionService(model_size=model_size)
        
        try:
            self.stdout.write('Processing audio...')
            result = transcription_service.process_audio(audio_file)
            
            # Format output for display
            self.stdout.write(self.style.SUCCESS('Transcription completed successfully!'))
            
            # Output results
            if output_file:
                try:
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    self.stdout.write(self.style.SUCCESS(f'Saved transcription to {output_file}'))
                except Exception as e:
                    raise CommandError(f'Error writing to output file: {e}')
            else:
                self.stdout.write(self.style.SUCCESS('Transcription results:'))
                self.stdout.write('\nFull text:')
                self.stdout.write(result['text'])
                
                self.stdout.write('\nSegments by speaker:')
                for segment in result['segments']:
                    speaker = segment.get('speaker', 'UNKNOWN')
                    start = segment.get('start', 0)
                    end = segment.get('end', 0)
                    text = segment.get('text', '')
                    
                    self.stdout.write(f"[{start:.2f}s - {end:.2f}s] {speaker}: {text}")
                
        except Exception as e:
            raise CommandError(f'Error transcribing audio: {e}')