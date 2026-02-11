import librosa
import numpy as np
import json

class AudioAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.y, self.sr = librosa.load(file_path)

    def get_bpm(self):
        tempo, _ = librosa.beat.beat_track(y=self.y, sr=self.sr)
        return float(tempo)

    def get_key(self):
        chroma = librosa.feature.chroma_cens(y=self.y, sr=self.sr)
        key_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        # Simplified key detection (find root)
        root_idx = np.argmax(np.mean(chroma, axis=1))
        return key_map[root_idx]

    def analyze_for_co_producer(self):
        # Returns data structure for sample matching
        return {
            "bpm": self.get_bpm(),
            "key": self.get_key(),
            "duration": librosa.get_duration(y=self.y, sr=self.sr)
        }
