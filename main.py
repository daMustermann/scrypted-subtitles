import sys
print("DEBUG: Loading scrypted-subtitles main.py", file=sys.stderr)

try:
    import scrypted_sdk
    from scrypted_sdk import ScryptedDeviceBase, DeviceProvider, ScryptedDeviceType, Setting, ScryptedInterface, ScryptedMimeTypes
    from stt_engine import STTEngine
    from database import SubtitleDatabase
    from http_server import HttpServer
    import asyncio
    import os
    import time
    print("DEBUG: Imports successful", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Import failed: {e}", file=sys.stderr)
    raise

class SubtitlesPlugin(ScryptedDeviceBase, DeviceProvider):
    def __init__(self, nativeId=None):
        print(f"DEBUG: SubtitlesPlugin init for {nativeId}", file=sys.stderr)
        super().__init__(nativeId=nativeId)
        self.db = SubtitleDatabase(os.path.join(os.path.dirname(__file__), 'subtitles.db'))
        self.db.init_db()
        self.http_server = HttpServer(self.db)
        asyncio.create_task(self.http_server.start())

    def getDevice(self, nativeId):
        return SubtitlesCameraExtension(nativeId, self.db)

class SubtitlesCameraExtension(ScryptedDeviceBase):
    def __init__(self, nativeId, db):
        super().__init__(nativeId=nativeId)
        self.db = db
        self.stt_engine = STTEngine()
        self.stt_engine.set_callback(self.on_text)
        self.transcribing = False
        
        # Initialize settings
        self.update_settings()

    def update_settings(self):
        # Check if enabled in settings (mock logic for now as we don't have full settings UI hooked up yet)
        # In real app, we'd read from self.storage.getItem('enabled')
        pass

    def on_text(self, text):
        # Callback from STT engine
        timestamp = time.time()
        self.db.add_subtitle(self.nativeId, timestamp, text)
        
        # Publish to Scrypted Sensor interface
        self.value = text
        
        print(f"Subtitle [{self.nativeId}]: {text}")

    def start_transcription(self):
        if self.transcribing:
            return
        self.transcribing = True
        self.stt_engine.start()
        
        # Here we would request the audio stream from the camera
        # media = scrypted_sdk.systemManager.getDeviceById(self.nativeId)
        # audio_stream = media.getVideoStream(stream_options) ...
        # This part requires the actual Scrypted runtime to work.
        # For now, we assume the engine is started and waiting for data.
        print(f"Started transcription for {self.nativeId}")

    def stop_transcription(self):
        self.transcribing = False
        self.stt_engine.stop()
        print(f"Stopped transcription for {self.nativeId}")

def create_scrypted_plugin(nativeId=None):
    return SubtitlesPlugin(nativeId)
