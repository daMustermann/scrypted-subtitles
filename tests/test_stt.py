import unittest
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Mock sherpa_onnx before importing stt_engine
sys.modules['sherpa_onnx'] = MagicMock()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stt_engine import STTEngine

class TestSTTEngine(unittest.TestCase):
    def test_initialization(self):
        engine = STTEngine()
        self.assertIsNotNone(engine)
        
    def test_process_audio_dummy(self):
        engine = STTEngine()
        # Mock the recognizer to avoid needing actual models for this unit test
        engine.recognizer = MagicMock()
        engine.stream = MagicMock()
        engine.running = True
        
        # Generate 1 second of silence at 16kHz
        audio = np.zeros(16000, dtype=np.float32)
        
        # Should not raise exception
        engine.process_audio(audio)
        engine.stop()

if __name__ == '__main__':
    unittest.main()
