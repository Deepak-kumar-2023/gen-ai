from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="")

audio = client.text_to_speech.convert(
    text="hi",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2"
)

# option 2: process the audio bytes manually
for chunk in audio:
    if isinstance(chunk, bytes):
        print(chunk)