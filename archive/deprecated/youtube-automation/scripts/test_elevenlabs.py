"""
ElevenLabs API Test Script
Tests voice cloning and text-to-speech generation
"""

import os
import requests
from pathlib import Path

# Configuration
API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel

def list_voices():
    """List available voices including cloned voices"""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json()["voices"]
        print("Available voices:")
        for voice in voices:
            print(f"  - {voice['name']}: {voice['voice_id']}")
        return voices
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_voice_info(voice_id: str = None):
    """Get detailed info about a specific voice"""
    vid = voice_id or VOICE_ID
    url = f"https://api.elevenlabs.io/v1/voices/{vid}"
    headers = {"xi-api-key": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voice = response.json()
        print(f"Voice: {voice['name']}")
        print(f"  Category: {voice.get('category', 'N/A')}")
        print(f"  Labels: {voice.get('labels', {})}")
        return voice
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def generate_speech(text: str, output_path: str = "output/test_audio.mp3"):
    """Generate speech from text using ElevenLabs API"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,
            "use_speaker_boost": True
        }
    }

    print(f"Generating speech for {len(text)} characters...")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Audio saved to: {output_path}")
        print(f"File size: {len(response.content) / 1024:.2f} KB")
        return output_path
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def clone_voice(name: str, audio_files: list):
    """Clone a voice from audio samples (requires paid plan)"""
    url = "https://api.elevenlabs.io/v1/voices/add"

    headers = {"xi-api-key": API_KEY}

    files = [("files", (Path(f).name, open(f, "rb"), "audio/mpeg")) for f in audio_files]
    data = {"name": name, "description": "Cloned voice for YouTube Shorts"}

    print(f"Cloning voice '{name}' from {len(audio_files)} audio files...")
    response = requests.post(url, headers=headers, data=data, files=files)

    # Close file handles
    for _, file_tuple in files:
        file_tuple[1].close()

    if response.status_code == 200:
        voice_id = response.json()["voice_id"]
        print(f"Voice cloned successfully!")
        print(f"Voice ID: {voice_id}")
        print(f"Add this to your .env: ELEVENLABS_VOICE_ID={voice_id}")
        return voice_id
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_usage():
    """Get API usage/subscription info"""
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {"xi-api-key": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sub = response.json()
        print("Subscription Info:")
        print(f"  Tier: {sub.get('tier', 'N/A')}")
        print(f"  Characters used: {sub.get('character_count', 0):,} / {sub.get('character_limit', 0):,}")
        print(f"  Characters remaining: {sub.get('character_limit', 0) - sub.get('character_count', 0):,}")
        return sub
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Testing ElevenLabs API")
    print("=" * 50)

    if not API_KEY:
        print("ERROR: ELEVENLABS_API_KEY not set!")
        print("Run: export ELEVENLABS_API_KEY=your_key_here")
        exit(1)

    # Check usage/subscription
    print("\n1. Checking subscription...")
    get_usage()

    # List voices
    print("\n2. Listing available voices...")
    list_voices()

    # Get voice info
    print(f"\n3. Getting info for voice: {VOICE_ID}...")
    get_voice_info()

    # Test speech generation
    print("\n4. Testing speech generation...")
    test_text = """
    Stop taking zinc for testosterone unless you're actually deficient.
    A 2023 study found that zinc only raises testosterone in men who were low to begin with.
    Get your levels tested first.
    """

    generate_speech(test_text.strip())

    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)
