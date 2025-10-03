"""
CatGen 2.0 - Cat Genetics Registry Application
Main application entry point with improved systems
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Import the new application class
from core.application import create_application
from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("CatGen")
    app.setOrganizationName("CatGen")
    
    # Create CatGen application instance with all improvements
    catgen_app = create_application()
    
    # Create and show main window
    window = MainWindow(catgen_app)
    window.show()
    
    # Run application
    exit_code = app.exec()
    
    # Cleanup on exit
    catgen_app.cleanup()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()