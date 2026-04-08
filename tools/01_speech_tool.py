import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speechsdk

load_dotenv(override=True)

speech_region = os.getenv("SPEECH_REGION")
speech_resource_id = os.getenv("SPEECH_RESOURCE_ID")
print(f"SPEECH_REGION: {speech_region}")
print(f"SPEECH_RESOURCE_ID: {speech_resource_id}")

if not speech_region or not speech_resource_id:
    raise ValueError("SPEECH_REGION and SPEECH_RESOURCE_ID must be set.")

credential = DefaultAzureCredential()
aad_token = credential.get_token("https://cognitiveservices.azure.com/.default").token

authorization_token = f"aad#{speech_resource_id}#{aad_token}"

speech_config = speechsdk.SpeechConfig(
    auth_token=authorization_token,
    region=speech_region,
)

speech_config.speech_synthesis_voice_name = "en-US-JennyMultilingualNeural"
#speech_config.speech_synthesis_voice_name = "hu-HU-NoemiNeural"

output_wav = "tts_output.wav"
audio_config = speechsdk.audio.AudioConfig(filename=output_wav)
synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config,
)

# The text we want to convert into speech
sample_text = (
    "Azure AI Speech can convert text into natural-sounding audio, "
    "generate richer narration from SSML, and transcribe spoken content "
    "back into text. This sample validates all three steps in a single run: "
    "text to speech, SSML synthesis, and speech to text."
)

result = synthesizer.speak_text_async(sample_text).get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("OK")
    print(f"Audio saved to {output_wav}")
else:
    print(result.reason)
    c = result.cancellation_details
    print(c.reason)
    print(c.error_code)
    print(c.error_details)

# Define SSML with pauses and emphasis
ssml_content = """
<speak version="1.0" xml:lang="en-US">
    <voice name="en-US-JennyMultilingualNeural">
        Welcome to this amazing course.
        <break strength="medium" />
        In this video, we explore how to convert text into
        natural-sounding speech using the Speech service in Foundry tools.
        <break />
        Let's get started!
    </voice>
</speak>
"""

# SSMSL allows us to add pauses, emphasis, and other speech effects to make the audio more engaging.
# Save to a different file so we can compare
ssml_output_wav = "ssml_output.wav"
ssml_audio_config = speechsdk.audio.AudioConfig(filename=ssml_output_wav)

ssml_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=ssml_audio_config
)
ssml_result = ssml_synthesizer.speak_ssml_async(ssml_content).get()

if ssml_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(f"SSML audio saved to {ssml_output_wav}")
else:
    print(f"SSML synthesis failed: {ssml_result.reason}")

# Speech to text
# Point the recognizer at the WAV file we created earlier
speech_config.speech_recognition_language = "en-US"
audio_input = speechsdk.AudioConfig(filename="tts_output.wav")

recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, audio_config=audio_input
)

stt_result = recognizer.recognize_once_async().get()

if stt_result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Transcription successful!")
    print(f"Text: {stt_result.text}")
else:
    print(f"Transcription failed: {stt_result.reason}")

# Optionally save the transcription to a file
with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write(stt_result.text)
    print("Saved to transcription.txt")
