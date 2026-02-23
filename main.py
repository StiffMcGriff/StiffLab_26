"""
OMNI-STUDIO AI - PRODUCTION SUITE
===================================
ARCHITECT & LEAD ENGINEER: Stiff McGriff
STATUS: ACTIVE DEVELOPMENT
VERSION: 1.0.0 (ALPHA)
"""

import os
import sys
from importlib.util import find_spec

# --- System Path Configuration ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Check if required libraries are installed before launching the GUI."""
    required = {
        "PyQt6": "GUI Framework",
        "matchering": "AI Mastering",
        "librosa": "Audio Analysis",
        "numpy": "Math Operations",
        "soundfile": "Audio I/O",
    }
    stem_providers = ("demucs", "spleeter")

    missing = []
    install_modules = []

    for module, description in required.items():
        if find_spec(module) is None:
            missing.append(f"{description} ({module})")
            install_modules.append(module)

    if all(find_spec(module) is None for module in stem_providers):
        missing.append("Stem Separation (demucs or spleeter)")
        install_modules.append("demucs")

    if missing:
        print("=" * 60)
        print("MISSING DEPENDENCIES DETECTED")
        print("=" * 60)
        print("The following libraries are required but not installed:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease install them by running:")
        print("  pip install " + " ".join(install_modules))
        print("=" * 60)
        return False
    return True


def main():
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)

    try:
        from PyQt6.QtWidgets import QApplication
        from gui.studio_ui import StudioWindow
    except ImportError as error:
        print(f"Fatal Error: Could not load GUI modules. {error}")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Stiff'sLab26")
    app.setApplicationVersion("1.0.0 Alpha")
    app.setOrganizationName("Stiff McGriff Productions")

    window = StudioWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
