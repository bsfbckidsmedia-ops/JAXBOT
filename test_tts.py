from aiavatarkit import TextToSpeech

try:
    tts = TextToSpeech()
    tts.synthesize("Hello world", "test.wav")
    print("TTS test passed - audio file generated")
except Exception as e:
    print(f"TTS test failed: {e}")