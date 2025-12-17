import sherpa_onnx
import numpy as np
import threading
import queue

class STTEngine:
    def __init__(self, model_path=None, tokens_path=None):
        # Default to a small model if not provided (placeholder paths)
        # In a real scenario, we'd download these or bundle them.
        # For N100, we use int8 quantized models.
        self.recognizer = None
        self.stream = None
        self.running = False
        self.audio_queue = queue.Queue()
        self.thread = None
        self.on_text_callback = None

    def initialize(self, model_dir):
        # Configuration for sherpa-onnx streaming recognizer
        # This is a generic config, specific model paths would be needed
        tokens = f"{model_dir}/tokens.txt"
        encoder = f"{model_dir}/encoder-epoch-99-avg-1.int8.onnx"
        decoder = f"{model_dir}/decoder-epoch-99-avg-1.int8.onnx"
        joiner = f"{model_dir}/joiner-epoch-99-avg-1.int8.onnx"
        
        # Check if files exist, if not, we might need to download them
        # For now, we assume they are present or will be provided
        
        self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=tokens,
            encoder=encoder,
            decoder=decoder,
            joiner=joiner,
            num_threads=1,
            sample_rate=16000,
            feature_dim=80,
            decoding_method="greedy_search",
        )
        self.stream = self.recognizer.create_stream()

    def set_callback(self, callback):
        self.on_text_callback = callback

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._process_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def process_audio(self, audio_data):
        # audio_data should be a numpy array of float32
        if self.running:
            self.audio_queue.put(audio_data)

    def _process_loop(self):
        while self.running:
            try:
                # Get audio chunk with timeout to allow checking self.running
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # Accept waveform
                self.stream.accept_waveform(16000, audio_chunk)
                
                # Decode
                while self.recognizer.is_ready(self.stream):
                    self.recognizer.decode_stream(self.stream)
                
                # Get result
                result = self.recognizer.get_result(self.stream)
                if result and len(result) > 0:
                    # In a real streaming scenario, we need to handle partial vs final results
                    # For simplicity, we just callback with whatever we have if it's new
                    if self.on_text_callback:
                        self.on_text_callback(result)
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"STT Error: {e}")

