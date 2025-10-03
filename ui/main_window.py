"""
Main application window with integrated improvements
"""

from PySide6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog, 
                               QMessageBox, QInputDialog)
from PySide6.QtGui import QAction
from PySide6.QtCore import QTimer
from pathlib import Path
import logging

from core.events import EventType
from ui.registry_tab import RegistryTab
from ui.breeding_tab import BreedingTab
from ui.generation_tab import GenerationTab
from ui.admin_tab import AdminTab

logger = logging.getLogger('catgen.ui')


class MainWindow(QMainWindow):
    """
    Main application window with integrated CatGen 2.0 improvements
    
    Features:
    - Event-driven updates
    - Service layer integration
    - Database synchronization
    - Advanced analytics
    - Comprehensive validation
    - Auto-save functionality
    """
    
    def __init__(self, app):
        super().__init__()
        
        # Store application instance
        self.app = app
        
        # Access subsystems (backward compatibility)
        self.genetics_engine = app.genetics_engine
        self.phenotype_calculator = app.phenotype_calculator
        self.breeding_engine = app.breeding_engine
        self.registry = app.registry
        
        # Access new services
        self.cat_service = app.cat_service
        self.breeding_service = app.breeding_service
        
        # Setup window
        self.setWindowTitle(f"{app.config.app_name} v{app.config.version}")
        self.setGeometry(100, 100, app.config.ui.window_width, app.config.ui.window_height)
        
        # Setup UI components
        self.setup_menu()
        self.setup_tabs()
        self.setup_statusbar()
        
        # Setup event handlers
        self.setup_event_handlers()
        
        # Auto-save timer
        if app.config.ui.auto_save_enabled:
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save)
            self.auto_save_timer.start(app.config.ui.auto_save_interval_seconds * 1000)
        
        # Apply stylesheet
        self.apply_stylesheet()
        
        logger.info("Main window initialized")
    
    def setup_event_handlers(self):
        """Setup event subscriptions for UI updates"""
        # Registry changes
        self.app.event_bus.subscribe(EventType.CAT_ADDED, self.on_registry_changed)
        self.app.event_bus.subscribe(EventType.CAT_UPDATED, self.on_registry_changed)
        self.app.event_bus.subscribe(EventType.CAT_DELETED, self.on_registry_changed)
        self.app.event_bus.subscribe(EventType.LITTER_SAVED, self.on_registry_changed)
        
        # File operations
        self.app.event_bus.subscribe(EventType.REGISTRY_LOADED, self.on_registry_loaded)
        self.app.event_bus.subscribe(EventType.REGISTRY_SAVED, self.on_registry_saved)
        
        # Modification tracking
        self.app.event_bus.subscribe(EventType.REGISTRY_MODIFIED, self.on_registry_modified)
    
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
        
        # Export submenu
        export_menu = file_menu.addMenu("📤 Export")
        
        export_report_action = QAction("Export Analytics Report...", self)
        export_report_action.triggered.connect(self.export_analytics_report)
        export_menu.addAction(export_report_action)
        
        export_json = QAction("Export as JSON...", self)
        export_json.triggered.connect(lambda: self.save_registry_as())
        export_menu.addAction(export_json)
        
        file_menu.addSeparator()
        
        backup_action = QAction("💾 Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        validate_action = QAction("✓ Validate Registry", self)
        validate_action.setShortcut("Ctrl+V")
        validate_action.triggered.connect(self.validate_registry)
        edit_menu.addAction(validate_action)
        
        edit_menu.addSeparator()
        
        prefs_action = QAction("&Preferences...", self)
        prefs_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(prefs_action)
        
        # Analytics menu (NEW!)
        analytics_menu = menubar.addMenu("📊 &Analytics")
        
        diversity_action = QAction("Genetic Diversity Report", self)
        diversity_action.triggered.connect(self.show_diversity_report)
        analytics_menu.addAction(diversity_action)
        
        inbreeding_action = QAction("Inbreeding Analysis", self)
        inbreeding_action.triggered.connect(self.show_inbreeding_analysis)
        analytics_menu.addAction(inbreeding_action)
        
        stats_action = QAction("Population Statistics", self)
        stats_action.setShortcut("Ctrl+I")
        stats_action.triggered.connect(self.show_statistics)
        analytics_menu.addAction(stats_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("⌨️ Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tabs(self):
        """Create tabbed interface"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs (pass main_window for backward compatibility)
        self.registry_tab = RegistryTab(self)
        self.breeding_tab = BreedingTab(self)
        self.generation_tab = GenerationTab(self)
        self.admin_tab = AdminTab(self)
        
        # Add tabs
        self.tabs.addTab(self.registry_tab, "📋 Registry")
        self.tabs.addTab(self.breeding_tab, "🧬 Breeding")
        self.tabs.addTab(self.generation_tab, "🎲 Generation")
        self.tabs.addTab(self.admin_tab, "⚙️ Admin")
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def setup_statusbar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")
        self.update_statusbar()
    
    def update_statusbar(self):
        """Update status bar with registry statistics"""
        try:
            stats = self.app.get_statistics()
            
            status_text = (
                f"Total: {stats.get('total', 0)} | "
                f"Males: {stats.get('males', 0)} | "
                f"Females: {stats.get('females', 0)} | "
                f"Effective Size: {stats.get('diversity', {}).get('effective_size', 0):.0f}"
            )
            
            if self.app.is_modified:
                status_text += " | ⚠️ Modified"
            
            self.statusBar().showMessage(status_text)
        except Exception as e:
            # Fallback to simple status
            cat_count = len(self.registry.cats) if self.registry else 0
            males = sum(1 for cat in self.registry.cats.values() if cat.sex == 'male') if self.registry else 0
            females = cat_count - males
            
            status_text = f"Total: {cat_count} | Males: {males} | Females: {females}"
            if self.app.is_modified:
                status_text += " | ⚠️ Modified"
            
            self.statusBar().showMessage(status_text)
    
    def on_tab_changed(self, index):
        """Handle tab changes"""
        # Refresh breeding tab when switched to
        if index == 1:  # Breeding tab
            self.breeding_tab.refresh_parent_lists()
    
    def on_registry_changed(self, event):
        """Handle registry changes (event-driven)"""
        self.registry_tab.refresh_table()
        self.update_statusbar()
    
    def on_registry_loaded(self, event):
        """Handle registry loaded event"""
        data = event.data
        self.statusBar().showMessage(
            f"✓ Loaded {data['cat_count']} cats from {Path(data['filepath']).name}",
            5000
        )
        self.registry_tab.refresh_table()
        self.update_statusbar()
        self.update_window_title()
    
    def on_registry_saved(self, event):
        """Handle registry saved event"""
        data = event.data
        self.statusBar().showMessage(
            f"✓ Saved {data['cat_count']} cats to {Path(data['filepath']).name}",
            5000
        )
        self.update_window_title()
    
    def on_registry_modified(self, event):
        """Handle registry modification"""
        self.update_statusbar()
        self.update_window_title()
    
    def update_window_title(self):
        """Update window title with file and modified status"""
        title = f"{self.app.config.app_name} v{self.app.config.version}"
        
        if self.app.current_file:
            title += f" - {self.app.current_file.name}"
        
        if self.app.is_modified:
            title += " *"
        
        self.setWindowTitle(title)
    
    def new_registry(self):
        """Create a new registry"""
        if self.check_unsaved_changes():
            self.registry.clear()
            self.app.current_file = None
            self.app.is_modified = False
            self.registry_tab.refresh_table()
            self.update_statusbar()
            self.update_window_title()
            self.statusBar().showMessage("New registry created", 3000)
    
    def load_registry(self):
        """Load registry from JSON file"""
        if not self.check_unsaved_changes():
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Registry",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            if self.app.load_registry(Path(filename)):
                # Event handlers will update UI
                pass
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to load registry. Check logs for details."
                )
    
    def save_registry(self):
        """Save registry to current file or prompt for location"""
        if self.app.current_file:
            self.app.save_registry()
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
            filepath = Path(filename)
            if self.app.save_registry(filepath):
                # Event handlers will update UI
                pass
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to save registry. Check logs for details."
                )
    
    def auto_save(self):
        """Auto-save if modified and file is set"""
        if self.app.is_modified and self.app.current_file:
            logger.info("Auto-saving registry")
            self.app.save_registry()
    
    def export_analytics_report(self):
        """Export comprehensive analytics report"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Analytics Report",
            "analytics_report.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            if self.app.export_report(Path(filename), include_analytics=True):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Analytics report exported to {Path(filename).name}"
                )
            else:
                QMessageBox.critical(self, "Error", "Failed to export report")
    
    def backup_database(self):
        """Create database backup"""
        if self.app.backup_database():
            QMessageBox.information(self, "Success", "Database backup created")
        else:
            QMessageBox.warning(self, "No Database", "No database to backup")
    
    def validate_registry(self):
        """Run comprehensive validation"""
        results = self.app.validate_all()
        
        summary = results['summary']
        
        if summary['is_valid']:
            QMessageBox.information(
                self,
                "Validation Passed",
                f"✓ Registry is valid!\n\n"
                f"Checked {len(self.registry)} cats with no errors."
            )
        else:
            error_text = (
                f"⚠️ Validation found issues:\n\n"
                f"Errors: {summary['total_errors']}\n"
                f"Warnings: {summary['total_warnings']}\n"
                f"Cats with errors: {summary['cats_with_errors']}\n\n"
                f"Check logs for details."
            )
            QMessageBox.warning(self, "Validation Issues", error_text)
    
    def show_diversity_report(self):
        """Show genetic diversity analysis"""
        report = self.app.diversity_analyzer.diversity_report()
        
        text = "🧬 Genetic Diversity Report\n"
        text += "=" * 60 + "\n\n"
        
        # Population size
        pop = report['population_size']
        text += f"Total Population: {pop['total_population']}\n"
        text += f"Effective Population Size (Ne): {pop['effective_size']:.1f}\n"
        text += f"Breeding Population: {pop['breeding_males']} males, {pop['breeding_females']} females\n\n"
        
        # Diversity
        summary = report['summary']
        text += f"Mean Heterozygosity: {summary['mean_heterozygosity']:.1%}\n"
        text += f"Status: {summary['diversity_status']}\n\n"
        
        # Rare alleles
        text += f"Rare Alleles (< 5%): {summary['total_rare_alleles']}\n"
        
        # Show in dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Genetic Diversity Report")
        msg.setText(text)
        msg.setDetailedText(str(report))
        msg.exec()
    
    def show_inbreeding_analysis(self):
        """Show inbreeding analysis"""
        inbred_cats = self.app.inbreeding_calculator.find_inbred_cats(threshold=0.0625)
        
        text = "⚠️ Inbreeding Analysis\n"
        text += "=" * 60 + "\n\n"
        
        if not inbred_cats:
            text += "✓ No inbred cats found (F > 6.25%)\n"
        else:
            text += f"Found {len(inbred_cats)} inbred cat(s):\n\n"
            
            for cat_info in inbred_cats[:10]:  # Show first 10
                text += f"#{cat_info['id']} {cat_info['name']}\n"
                text += f"  F = {cat_info['percentage']:.1f}%\n"
                text += f"  {cat_info['relationship']}\n"
                text += f"  Common ancestors: {len(cat_info['common_ancestors'])}\n\n"
            
            if len(inbred_cats) > 10:
                text += f"... and {len(inbred_cats) - 10} more\n"
        
        QMessageBox.information(self, "Inbreeding Analysis", text)
    
    def show_statistics(self):
        """Show population statistics"""
        try:
            stats = self.app.get_statistics()
            
            text = "📊 Population Statistics\n"
            text += "=" * 60 + "\n\n"
            text += f"Total Cats: {stats.get('total', 0)}\n"
            text += f"Males: {stats.get('males', 0)}\n"
            text += f"Females: {stats.get('females', 0)}\n"
            text += f"Founders: {stats.get('founders', 0)}\n"
            text += f"With Parents: {stats.get('with_parents', 0)}\n\n"
            
            if stats.get('generations'):
                text += "Generations:\n"
                for gen, count in sorted(stats['generations'].items()):
                    text += f"  Gen {gen}: {count} cats\n"
                text += "\n"
            
            diversity = stats.get('diversity', {})
            text += f"Effective Population Size: {diversity.get('effective_size', 0):.1f}\n"
            text += f"Mean Heterozygosity: {diversity.get('mean_heterozygosity', 0):.1%}\n"
            
            inbreeding = stats.get('inbreeding', {})
            text += f"\nInbred Cats: {inbreeding.get('count', 0)} ({inbreeding.get('percentage', 0):.1f}%)\n"
            
            QMessageBox.information(self, "Population Statistics", text)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not calculate statistics:\n{str(e)}\n\nCheck logs for details."
            )
    
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences dialog
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog coming soon!\n\n"
            "Current config location:\n"
            f"{Path('config/settings.json').absolute()}"
        )
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """
        Keyboard Shortcuts:
        
        File Operations:
          Ctrl+N        New Registry
          Ctrl+O        Open Registry
          Ctrl+S        Save Registry
          Ctrl+Shift+S  Save Registry As
          Ctrl+Q        Exit
        
        Editing:
          Ctrl+E        Add Entity
          Ctrl+V        Validate Registry
          Delete        Delete Selected
          Ctrl+D        Duplicate
        
        View:
          Ctrl+F        Advanced Search
          Ctrl+I        Statistics
        
        Tools:
          Ctrl+T        Create from Template
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>{self.app.config.app_name} v{self.app.config.version}</h2>
        <p><b>Advanced Cat Genetics Registry & Breeding Simulator</b></p>
        
        <h3>Features:</h3>
        <ul>
            <li>Complete Mendelian genetics simulation</li>
            <li>Advanced breeding predictions</li>
            <li>Genetic diversity analysis</li>
            <li>Inbreeding coefficient calculation</li>
            <li>Database-backed storage</li>
            <li>Comprehensive validation</li>
        </ul>
        
        <p><i>Built with PySide6</i></p>
        """
        QMessageBox.about(self, "About CatGen", about_text)
    
    def check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user"""
        if not self.app.is_modified:
            return True
        
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save before continuing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Save:
            self.save_registry()
            return True
        elif reply == QMessageBox.Discard:
            return True
        else:
            return False
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.check_unsaved_changes():
            # Cleanup application
            self.app.cleanup()
            event.accept()
        else:
            event.ignore()
    
    def apply_stylesheet(self):
        """Apply custom stylesheet"""
        # Dark theme stylesheet
        if self.app.config.ui.theme == "dark":
            DARK_THEME = """
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
            self.setStyleSheet(DARK_THEME)