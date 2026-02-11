from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class MusicPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_song_index = 0
        self.songs = []  # List of file paths
        
        # Setup Media Player (The engine)
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Setup UI
        self.setup_ui()
        
        # Connect Signals (The "Event Listeners" of Python)
        self.media_player.positionChanged.connect(self.update_progress)
        self.media_player.playbackStateChanged.connect(self.update_play_button_text)

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Buttons
        self.btn_prev = QPushButton("Previous")
        self.btn_play_pause = QPushButton("Play")
        self.btn_next = QPushButton("Next")
        
        # Progress Bar
        self.progress_bar = QSlider()
        self.progress_bar.setRange(0, 100)
        
        # Layout
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_prev)
        controls_layout.addWidget(self.btn_play_pause)
        controls_layout.addWidget(self.btn_next)
        
        layout.addWidget(self.progress_bar)
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # Connect Clicks (Logic)
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        self.btn_next.clicked.connect(self.next_song)
        self.btn_prev.clicked.connect(self.prev_song)
        self.progress_bar.sliderMoved.connect(self.set_position)

    def load_songs(self, song_list):
        self.songs = song_list
        if self.songs:
            self.load_song(0)

    def load_song(self, index):
        if 0 <= index < len(self.songs):
            self.current_song_index = index
            url = QUrl.fromLocalFile(self.songs[self.current_song_index])
            self.media_player.setSource(url)

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_play_button_text(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play_pause.setText("Pause")
        else:
            self.btn_play_pause.setText("Play")

    def next_song(self):
        if not self.songs: return
        self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        self.load_song(self.current_song_index)
        self.media_player.play()

    def prev_song(self):
        if not self.songs: return
        self.current_song_index = (self.current_song_index - 1 + len(self.songs)) % len(self.songs)
        self.load_song(self.current_song_index)
        self.media_player.play()

    def update_progress(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            value = int((position / duration) * 100)
            self.progress_bar.setValue(value)

    def set_position(self, value):
        duration = self.media_player.duration()
        if duration > 0:
            pos = int((value / 100) * duration)
            self.media_player.setPosition(pos)
