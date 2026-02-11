"""
OMNI-STUDIO AI - PRODUCTION SUITE
===================================
ARCHITECT & LEAD ENGINEER: Stiff McGriff
STATUS: ACTIVE DEVELOPMENT
VERSION: 1.0.0 (ALPHA)

DESCRIPTION:
A free, open-source, AI-powered Digital Audio Workstation (DAW) 
that rivals industry standards like DaVinci Resolve, LANDR, and Ableton, 
built entirely from scratch using Python, PyQt6, and open-source AI models.

CORE CAPABILITIES:
- AI Mastering (Matchering 2.0)
- Stem Separation (Spleeter/Demucs)
- Audio Analysis (BPM/Key/Harmonic)
- Generative Music (Riffusion/ACE-Step)
- VST Hosting & Scanning
- Sample Suggestion Engine (Co-Producer mimic)

COPYRIGHT © 2024 Stiff McGriff. All rights reserved.
"""

# ... (top of file) ...
import sys
import os

# --- System Path Configuration ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Import GUI (MUST BE AFTER PATH SETUP) ---
try:
    from PyQt6.QtWidgets import QApplication
    # CHANGE THIS LINE to point to gui folder:
    from gui.studio_ui import StudioWindow 
except ImportError as e:
    print(f"Fatal Error: Could not load GUI. Did you move studio_ui.py to the gui folder? Error: {e}")
    sys.exit(1)
# ... (rest of main.py) ...
import sys
import os

# --- System Path Configuration ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Dependency Check ---
def check_dependencies():
    """Checks if required libraries are installed before launching GUI."""
    required = {
        "PyQt6": "GUI Framework",
        "matchering": "AI Mastering",
        "spleeter": "Stem Separation",
        "librosa": "Audio Analysis",
        "numpy": "Math Operations",
        "soundfile": "Audio I/O"
    }
    
    missing = []
    for module, desc in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(f"{desc} ({module})")
    
    if missing:
        print("=" * 60)
        print("❌ MISSING DEPENDENCIES DETECTED")
        print("=" * 60)
        print("The following libraries are required but not installed:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease install them by running:")
        print("  pip install " + " ".join([m.split(' ')[0] for m in missing]))
        print("=" * 60)
        return False
    return True

# --- Application Launch ---
def main():
    # 1. Check if system is ready
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)

    # 2. Import GUI 
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.studio_ui import StudioWindow
    except ImportError as e:
        print(f"Fatal Error: Could not load GUI modules. {e}")
        sys.exit(1)

    # 3. Initialize Qt Application
    app = QApplication(sys.argv)
    
    # Set Application Metadata (YOUR BRAND)
    app.setApplicationName("Omni-Studio AI")
    app.setApplicationVersion("1.0.0 Alpha")
    app.setOrganizationName("Stiff McGriff Productions")
    
    # Dark Fusion Stylesheet
    app.setStyleSheet("""
        QMainWindow { background-color: #1e1e1e; }
        QTabWidget::pane { border: 1px solid #333; }
        QTabBar::tab { 
            background: #2d2d2d; 
            color: #fff; 
            padding: 10px; 
            border: 1px solid #333;
        }
        QTabBar::tab:selected { background: #ff3b30; } 
        QPushButton { 
            background-color: #2d2d2d; 
            color: white; 
            border: 1px solid #555; 
            padding: 8px; 
            border-radius: 4px;
        }
        QPushButton:hover { background-color: #3d3d3d; }
        QPushButton:pressed { background-color: #1d1d1d; }
        QLabel { color: #fff; }
        QLineEdit { 
            background: #2d2d2d; 
            border: 1px solid #555; 
            color: white; 
            padding: 5px;
        }
    """)

    # 4. Create and Show Main Window
    window = StudioWindow()
    window.show()

    # 5. Run Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


