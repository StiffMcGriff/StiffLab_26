# gui/studio_ui.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Callable, Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPalette, QBrush
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Local UI widgets
from gui.player_ui import MusicPlayerWidget
from gui.custom_widgets import MPC_Pad, NeonFader, NeonKnob, VUMeter

# Core engines
from core.mastering import MasteringEngine
from core.analyzer import AudioAnalyzer
from core.separator import StemSeparator
from core.voicebox_plugin import VoiceboxPlugin


AUDIO_FILTER = "Audio (*.wav *.mp3 *.flac *.aiff *.aif *.ogg *.m4a)"


def ensure_parent_dir(output_path: str) -> None:
    out = Path(output_path).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)


def pick_audio_file(parent: QWidget, title: str) -> str:
    path, _ = QFileDialog.getOpenFileName(parent, title, "", AUDIO_FILTER)
    return path or ""


def safe_call_master(
    engine: Any, target: str, reference: str, output: str
) -> Tuple[bool, str]:
    """
    Supports either MasteringEngine.master(...) or MasteringEngine.process(...).
    """
    ensure_parent_dir(output)
    if hasattr(engine, "master") and callable(getattr(engine, "master")):
        return engine.master(target, reference, output)
    if hasattr(engine, "process") and callable(getattr(engine, "process")):
        return engine.process(target, reference, output)
    return False, "MasteringEngine has no master() or process() method."


class StudioWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StiffsLab | Photorealistic Virtual Studio")
        self.setGeometry(100, 100, 1480, 820)
        self._setup_styles()

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.addLayout(self._create_header())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        root_layout.addWidget(self.tabs)

        self._init_rooms()

    def _setup_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background-color: #06090f; }
            QWidget { color: #e9f4ff; font-family: "Trebuchet MS", "Segoe UI", sans-serif; }
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #101a2a; border: 1px solid #2f4463; border-radius: 11px;
                padding: 8px 20px; margin: 4px 2px; min-width: 150px;
            }
            QTabBar::tab:selected { border: 1px solid #4ef6ff; }
            QGroupBox {
                border: 1px solid #304767; border-radius: 13px; margin-top: 10px;
                background: #111b2f;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 5px 10px; font-size: 11px; color: #b8d0eb;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #3a4f72; background: #101a2e; border-radius: 8px; padding: 4px;
            }
            QPushButton {
                border: 1px solid #3a4f72; border-radius: 8px; background: #1a2740; padding: 6px 10px;
            }
            QPushButton:hover { background: #223551; }
            """
        )

    def _create_header(self) -> QHBoxLayout:
        header_layout = QHBoxLayout()

        title = QLabel("StiffsLab | Photorealistic Virtual Studio")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        subtitle = QLabel("Five dedicated rooms, AI engines, piano lanes, and utility modules.")
        subtitle.setStyleSheet("font-size: 13px; color: #91a6c0;")

        title_col = QVBoxLayout()
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        transport = QHBoxLayout()
        transport.addWidget(QLabel("Bar 1 | Beat 1"))
        transport.addWidget(QLabel("BPM"))

        bpm = QSpinBox()
        bpm.setRange(40, 220)
        bpm.setValue(122)
        transport.addWidget(bpm)

        for text in ("Play", "Pause", "Stop", "Record"):
            transport.addWidget(QPushButton(text))

        header_layout.addLayout(title_col)
        header_layout.addStretch()
        header_layout.addLayout(transport)
        return header_layout

    def _init_rooms(self) -> None:
        self.tabs.addTab(MainControlRoom(self), "Main Control Room")
        self.tabs.addTab(
            ImageRoom(
                "Vocal Booth",
                "Live visualization, auto-tune, pitch correction, harmony generation",
                "assets/rooms/vocal_room.png",
            ),
            "Vocal Booth",
        )
        self.tabs.addTab(
            ImageRoom("Drum Room", "Interactive triggers and per-drum controls", "assets/rooms/drum_room.png"),
            "Drum Room",
        )
        self.tabs.addTab(
            ImageRoom(
                "Instrument Room",
                "AI orchestrator and arrangement workflow",
                "assets/rooms/instrument_room.png",
            ),
            "Instrument Room",
        )
        self.tabs.addTab(VibeChambers(self), "Vibe Chambers")


class MainControlRoom(QWidget):
    def __init__(self, parent_window: StudioWindow) -> None:
        super().__init__()
        self.parent_window = parent_window

        self.mastering_engine = MasteringEngine()
        self.stem_separator = StemSeparator()
        self.voicebox_plugin = VoiceboxPlugin()

        main_grid = QGridLayout(self)
        main_grid.setColumnStretch(0, 2)
        main_grid.setColumnStretch(1, 1)

        left_group = QGroupBox("Professional Mixing Console")
        left_layout = QVBoxLayout(left_group)
        left_layout.addLayout(self._build_console_layout())

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QGroupBox("Audio Track Lanes"))
        bottom_layout.addWidget(QGroupBox("User Piano Roll"))
        left_layout.addLayout(bottom_layout)

        right_group = QGroupBox("AI & Utility Modules")
        right_layout = QVBoxLayout(right_group)
        right_layout.addWidget(self._build_file_panel())
        right_layout.addWidget(self._build_engine_panel())
        right_layout.addWidget(self._build_pad_panel())
        right_layout.addStretch()

        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(right_group, 0, 1)

    def _build_console_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        for strip_name in ("VOC", "DRM", "BASS", "SYN", "FX1", "FX2", "BUS", "MST"):
            strip = QVBoxLayout()
            name_label = QLabel(strip_name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            strip.addWidget(name_label)
            strip.addWidget(VUMeter(), alignment=Qt.AlignmentFlag.AlignCenter)
            strip.addWidget(NeonKnob("GAIN"), alignment=Qt.AlignmentFlag.AlignCenter)
            strip.addWidget(NeonFader("VOL"), alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addLayout(strip)
        return layout

    def _build_file_panel(self) -> QFrame:
        panel = QFrame()
        panel_layout = QVBoxLayout(panel)
        panel_layout.addWidget(QLabel("Audio Sources"))

        self.target_path = QLineEdit()
        self.target_path.setPlaceholderText("Target mix path")

        self.reference_path = QLineEdit()
        self.reference_path.setPlaceholderText("Reference mix path")

        self.output_path = QLineEdit("output/mastered.wav")
        self.output_path.setPlaceholderText("Mastered output path")

        target_row = QHBoxLayout()
        target_row.addWidget(self.target_path)
        choose_target = QPushButton("Browse")
        choose_target.clicked.connect(lambda: self._pick_file_into(self.target_path))
        target_row.addWidget(choose_target)

        ref_row = QHBoxLayout()
        ref_row.addWidget(self.reference_path)
        choose_ref = QPushButton("Browse")
        choose_ref.clicked.connect(lambda: self._pick_file_into(self.reference_path))
        ref_row.addWidget(choose_ref)

        panel_layout.addLayout(target_row)
        panel_layout.addLayout(ref_row)
        panel_layout.addWidget(self.output_path)
        return panel

    def _build_engine_panel(self) -> QFrame:
        panel = QFrame()
        layout = QVBoxLayout(panel)
        row = QHBoxLayout()

        btn_analyze = QPushButton("Analyze")
        btn_analyze.clicked.connect(self.run_analysis)

        btn_master = QPushButton("Master")
        btn_master.clicked.connect(self.run_mastering)

        btn_separate = QPushButton("Separate Stems")
        btn_separate.clicked.connect(self.run_separation)

        btn_voicebox = QPushButton("Voicebox AI")
        btn_voicebox.clicked.connect(self.run_voicebox)

        row.addWidget(btn_analyze)
        row.addWidget(btn_master)
        row.addWidget(btn_separate)
        row.addWidget(btn_voicebox)

        self.lbl_bpm = QLabel("BPM: -")
        self.lbl_key = QLabel("Key: -")
        self.lbl_status = QLabel("Status: Ready")
        self.lbl_status.setStyleSheet("color: #91a6c0;")

        layout.addLayout(row)
        layout.addWidget(self.lbl_bpm)
        layout.addWidget(self.lbl_key)
        layout.addWidget(self.lbl_status)
        return panel

    def _build_pad_panel(self) -> QGroupBox:
        group = QGroupBox("MPC Drum Pads")
        grid = QGridLayout(group)
        for i in range(16):
            grid.addWidget(MPC_Pad(f"{i + 1}"), i // 4, i % 4)
        return group

    def _pick_file_into(self, field: QLineEdit) -> None:
        path = pick_audio_file(self, "Select audio file")
        if path:
            field.setText(path)

    def run_analysis(self) -> None:
        file_path = self.target_path.text().strip()
        if not file_path:
            file_path = pick_audio_file(self, "Select audio to analyze")
            if not file_path:
                return
            self.target_path.setText(file_path)

        try:
            analyzer = AudioAnalyzer(file_path)
            data = analyzer.analyze_for_co_producer()
            bpm = float(data["bpm"])
            key = str(data["key"])
            self.lbl_bpm.setText(f"BPM: {bpm:.2f}")
            self.lbl_key.setText(f"Key: {key}")
            self.lbl_status.setText("Status: Analysis complete")
        except Exception as exc:
            self.lbl_status.setText("Status: Analysis failed")
            QMessageBox.critical(self, "Analysis Failed", str(exc))

    def run_mastering(self) -> None:
        target = self.target_path.text().strip()
        reference = self.reference_path.text().strip()
        output = self.output_path.text().strip() or "output/mastered.wav"

        if not target or not reference:
            QMessageBox.warning(self, "Missing Inputs", "Choose both target and reference files.")
            return

        self.lbl_status.setText("Status: Mastering in progress...")
        QApplication.processEvents()

        ok, message = safe_call_master(self.mastering_engine, target, reference, output)
        self.lbl_status.setText(f"Status: {message}")

        if ok:
            QMessageBox.information(self, "Mastering Complete", message)
        else:
            QMessageBox.critical(self, "Mastering Failed", message)

    def run_separation(self) -> None:
        target = self.target_path.text().strip()
        if not target:
            QMessageBox.warning(self, "Missing Target", "Select a target file first.")
            return

        output_dir = str(Path("output") / "stems")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        self.lbl_status.setText("Status: Stem separation running...")
        QApplication.processEvents()

        try:
            ok, message = self.stem_separator.separate(target, output_dir)
        except Exception as exc:
            ok, message = False, str(exc)

        self.lbl_status.setText(f"Status: {message}")
        if ok:
            QMessageBox.information(self, "Separation Complete", message)
        else:
            QMessageBox.warning(self, "Separation Failed", message)

    def run_voicebox(self) -> None:
        target = self.target_path.text().strip()
        if not target:
            QMessageBox.warning(self, "Missing Target", "Select a target file first.")
            return

        self.lbl_status.setText("Status: Voicebox AI plugin running...")
        QApplication.processEvents()

        try:
            ok, message, output_path = self.voicebox_plugin.process(target)
        except Exception as exc:
            ok, message, output_path = False, str(exc), ""

        self.lbl_status.setText(f"Status: {message}")
        if ok:
            QMessageBox.information(self, "Voicebox Complete", f"{message}\nOutput: {output_path}")
        else:
            QMessageBox.warning(self, "Voicebox Failed", message)


class VibeChambers(QWidget):
    def __init__(self, parent_window: StudioWindow) -> None:
        super().__init__()
        self.parent_window = parent_window
        layout = QVBoxLayout(self)

        title = QLabel("VIBE CHAMBERS - GENERATIVE LAB")
        title.setStyleSheet("font-size: 24px; color: #aa00ff;")
        layout.addWidget(title)

        controls = QHBoxLayout()
        self.duration_knob = NeonKnob("DURATION", 10, 120, QColor(170, 0, 255))
        self.duration_knob.setValue(30)

        self.tempo_knob = NeonKnob("TEMPO", 60, 180, QColor(170, 0, 255))
        self.tempo_knob.setValue(120)

        controls.addWidget(self.duration_knob)
        controls.addWidget(self.tempo_knob)
        controls.addStretch()
        layout.addLayout(controls)

        self.btn_generate = QPushButton("Generate New Idea")
        self.btn_generate.clicked.connect(self.run_generation)

        self.lbl_status = QLabel("Status: Ready to dream...")
        self.player = MusicPlayerWidget()

        layout.addWidget(self.btn_generate)
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.player)

    def run_generation(self) -> None:
        try:
            from core.generator import MusicGenerator

            duration = int(getattr(self.duration_knob, "value", self.duration_knob.value()))
            tempo = int(getattr(self.tempo_knob, "value", self.tempo_knob.value()))

            generator = MusicGenerator()
            self.lbl_status.setText("Status: Dreaming up a track...")
            QApplication.processEvents()

            output = generator.generate_track(duration=duration, tempo_bpm=tempo)
            out_path = str(Path(output).resolve())

            self.player.load_songs([out_path])
            self.lbl_status.setText(f"Status: Manifested at {out_path}")
            QMessageBox.information(self, "Success", f"Track generated: {out_path}")
        except Exception as exc:
            self.lbl_status.setText("Status: Error")
            QMessageBox.critical(self, "Generation Failed", str(exc))


class ImageRoom(QWidget):
    def __init__(self, name: str, description: str, bg_image_path: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setAutoFillBackground(True)

        image = QImage(bg_image_path)
        if not image.isNull():
            palette = self.palette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(image))
            self.setPalette(palette)

        header = QGroupBox()
        header_layout = QVBoxLayout(header)

        title = QLabel(name)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e9f4ff; border: none;")

        desc = QLabel(description)
        desc.setStyleSheet("color: #91a6c0; border: none;")

        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        header.setStyleSheet("background: rgba(12, 19, 31, 0.84); border-radius: 12px; padding: 15px;")

        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addStretch()


def main() -> int:
    app = QApplication(sys.argv)
    window = StudioWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
