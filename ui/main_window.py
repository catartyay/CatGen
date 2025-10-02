"""
Main application window with tabbed interface
"""

from PySide6.QtWidgets import (QMainWindow, QTabWidget, QMenuBar, 
                               QMenu, QFileDialog, QMessageBox, QStatusBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from pathlib import Path
import json

from core.genetics_engine import GeneticsEngine
from core.phenotype_calculator import PhenotypeCalculator
from core.breeding import BreedingEngine
from data.registry import CatRegistry
from ui.registry_tab import RegistryTab
from ui.breeding_tab import BreedingTab
from ui.generation_tab import GenerationTab
from ui.admin_tab import AdminTab


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CatGen - Cat Genetics Registry")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize engines
        self.genetics_engine = GeneticsEngine()
        self.phenotype_calculator = PhenotypeCalculator(self.genetics_engine)
        self.breeding_engine = BreedingEngine(self.genetics_engine)
        self.registry = CatRegistry()
        
        # Setup UI
        self.setup_menu()
        self.setup_tabs()
        self.setup_statusbar()
        
        # Apply stylesheet
        self.apply_stylesheet()
    
    def setup_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Registry", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_registry)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Registry...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_registry)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Registry", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_registry)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Registry &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_registry_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        prefs_action = QAction("&Preferences...", self)
        prefs_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(prefs_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About CatGen", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
    
    def setup_tabs(self):
        """Create tabbed interface"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.registry_tab = RegistryTab(self)
        self.breeding_tab = BreedingTab(self)
        self.generation_tab = GenerationTab(self)
        self.admin_tab = AdminTab(self)
        
        # Add tabs
        self.tabs.addTab(self.registry_tab, "Registry")
        self.tabs.addTab(self.breeding_tab, "Breeding")
        self.tabs.addTab(self.generation_tab, "Generation")
        self.tabs.addTab(self.admin_tab, "Admin")
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def setup_statusbar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")
        self.update_statusbar()
    
    def update_statusbar(self):
        """Update status bar with registry statistics"""
        cat_count = len(self.registry.cats)
        male_count = sum(1 for cat in self.registry.cats.values() if cat.sex == 'male')
        female_count = cat_count - male_count
        self.statusBar().showMessage(
            f"Total Cats: {cat_count} | Males: {male_count} | Females: {female_count}"
        )
    
    def on_tab_changed(self, index):
        """Handle tab changes"""
        # Refresh breeding tab when switched to
        if index == 1:  # Breeding tab
            self.breeding_tab.refresh_parent_lists()
    
    def new_registry(self):
        """Create a new registry"""
        reply = QMessageBox.question(
            self, 
            "New Registry",
            "Create a new registry? Any unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.registry.clear()
            self.registry_tab.refresh_table()
            self.update_statusbar()
            self.statusBar().showMessage("New registry created", 3000)
    
    def load_registry(self):
        """Load registry from JSON file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Registry",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.registry.load_from_data(data)
                self.registry_tab.refresh_table()
                self.update_statusbar()
                self.statusBar().showMessage(f"Loaded {len(self.registry.cats)} cats", 3000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Loading Registry",
                    f"Failed to load registry:\n{str(e)}"
                )
    
    def save_registry(self):
        """Save registry to current file or prompt for location"""
        if hasattr(self.registry, 'current_file') and self.registry.current_file:
            self._save_to_file(self.registry.current_file)
        else:
            self.save_registry_as()
    
    def save_registry_as(self):
        """Save registry to a new file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Registry As",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            self._save_to_file(filename)
    
    def _save_to_file(self, filename):
        """Internal method to save registry to file"""
        try:
            data = self.registry.to_data()
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.registry.current_file = filename
            self.statusBar().showMessage(f"Saved {len(self.registry.cats)} cats", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving Registry",
                f"Failed to save registry:\n{str(e)}"
            )
    
    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog coming soon!"
        )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CatGen",
            "<h2>CatGen</h2>"
            "<p>Cat Genetics Registry Application</p>"
            "<p>Version 1.0</p>"
            "<p>A comprehensive tool for managing cat genetics, "
            "breeding, and phenotype visualization.</p>"
        )
    
    def show_documentation(self):
        """Show documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation is available in the README.md file."
        )
    
    def apply_stylesheet(self):
        """Apply custom stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 20px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #4CAF50;
        }
        
        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }
        
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #45a049;
        }
        
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #4CAF50;
        }
        
        QTableWidget {
            gridline-color: #e0e0e0;
            border: 1px solid #cccccc;
            background-color: white;
        }
        
        QTableWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #e8e8e8;
            padding: 6px;
            border: none;
            border-right: 1px solid #cccccc;
            border-bottom: 1px solid #cccccc;
            font-weight: bold;
        }
        
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
        }
        
        QComboBox:hover {
            border: 1px solid #4CAF50;
        }
        
        QSpinBox, QDoubleSpinBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
        }
        
        QGroupBox {
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 12px;
            font-weight: bold;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        """
        self.setStyleSheet(stylesheet)