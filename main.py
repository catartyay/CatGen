"""
CatGen - Cat Genetics Registry Application
Main application entry point
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CatGen")
    app.setOrganizationName("CatGen")
    
    # High DPI settings (these are deprecated but harmless)
    # You can remove these lines if you want to suppress the warnings
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()