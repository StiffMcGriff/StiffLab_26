from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys

# Import our core engines
from core.mastering import MasteringEngine
from core.analyzer import AudioAnalyzer

class MasterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Omni-Studio AI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Dark Theme
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        # Central Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Tab 1: Mastering ---
        self.mastering_tab = QWidget()
        self.tabs.addTab(self.mastering_tab, "Mastering Room")
        self.setup_mastering_ui()

        # --- Tab 2: Analysis ---
        self.analysis_tab = QWidget()
        self.tabs.addTab(self.analysis_tab, "Analysis Room")
        self.setup_analysis_ui()

    def setup_mastering_ui(self):
        layout = QVBoxLayout()
        
        # File Pickers
        self.target_input = QLineEdit()
        self.ref_input = QLineEdit()
        self.btn_target = QPushButton("Select Track to Master")
        self.btn_ref = QPushButton("Select Reference Track")
        self.btn_master = QPushButton("MASTER")
        self.btn_master.setStyleSheet("background-color: #ff3b30; font-weight: bold;")

        layout.addWidget(QLabel("Target Track:"))
        layout.addWidget(self.target_input)
        layout.addWidget(self.btn_target)
        
        layout.addWidget(QLabel("Reference Track (Style Match):"))
        layout.addWidget(self.ref_input)
        layout.addWidget(self.btn_ref)
        layout.addWidget(self.btn_master)

        # Connections
        self.btn_target.clicked.connect(lambda: self.file_dialog(self.target_input))
        self.btn_ref.clicked.connect(lambda: self.file_dialog(self.ref_input))
        self.btn_master.clicked.connect(self.run_mastering)

        self.mastering_tab.setLayout(layout)

    def setup_analysis_ui(self):
        layout = QVBoxLayout()
        self.btn_analyze = QPushButton("Analyze Track")
        self.lbl_bpm = QLabel("BPM: --")
        self.lbl_key = QLabel("Key: --")
        
        layout.addWidget(self.btn_analyze)
        layout.addWidget(self.lbl_bpm)
        layout.addWidget(self.lbl_key)
        
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.analysis_tab.setLayout(layout)

    def file_dialog(self, target_line_edit):
        file, _ = QFileDialog.getOpenFileName(self, "Open Audio", "", "Audio Files (*.wav *.mp3)")
        if file:
            target_line_edit.setText(file)

    def run_mastering(self):
        target = self.target_input.text()
        ref = self.ref_input.text()
        if not target or not ref:
            QMessageBox.warning(self, "Error", "Please select both tracks.")
            return
            
        engine = MasteringEngine()
        success, msg = engine.process(target, ref, "output/mastered.wav")
        QMessageBox.information(self, "Status", msg)

    def run_analysis(self):
        # Placeholder for file dialog logic
        file = "path/to/test.wav" # Replace with dialog
        if file:
            analyzer = AudioAnalyzer(file)
            data = analyzer.analyze_for_co_producer()
            self.lbl_bpm.setText(f"BPM: {data['bpm']:.2f}")
            self.lbl_key.setText(f"Key: {data['key']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())
