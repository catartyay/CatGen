"""
Registry tab - displays all cats in a searchable table
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                               QComboBox, QCheckBox, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from ui.dialogs.cat_details_dialog import CatDetailsDialog
from ui.dialogs.cat_editor_dialog import CatEditorDialog
from ui.dialogs.pedigree_dialog import PedigreeDialog


class RegistryTab(QWidget):
    """Registry view with search and filtering"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        """Create the registry interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Cat Registry")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Search and filter panel
        filter_group = QGroupBox("Search & Filter")
        filter_layout = QVBoxLayout()
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter ID, name, or phenotype...")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(self.search_input)
        filter_layout.addLayout(search_layout)
        
        # Filter controls
        filter_controls = QHBoxLayout()
        
        filter_controls.addWidget(QLabel("Sex:"))
        self.sex_filter = QComboBox()
        self.sex_filter.addItems(["All", "Male", "Female"])
        self.sex_filter.currentTextChanged.connect(self.apply_filters)
        filter_controls.addWidget(self.sex_filter)
        
        filter_controls.addWidget(QLabel("Fur:"))
        self.fur_filter = QComboBox()
        self.fur_filter.addItems(["All", "Shorthair", "Longhair"])
        self.fur_filter.currentTextChanged.connect(self.apply_filters)
        filter_controls.addWidget(self.fur_filter)
        
        self.has_parents = QCheckBox("Has Parents")
        self.has_parents.stateChanged.connect(self.apply_filters)
        filter_controls.addWidget(self.has_parents)
        
        self.has_offspring = QCheckBox("Has Offspring")
        self.has_offspring.stateChanged.connect(self.apply_filters)
        filter_controls.addWidget(self.has_offspring)
        
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        filter_controls.addWidget(clear_btn)
        
        filter_controls.addStretch()
        filter_layout.addLayout(filter_controls)
        
        # Results count
        self.results_label = QLabel()
        filter_layout.addWidget(self.results_label)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Cat table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Sex", "Phenotype", "Eye Color", "Build", "Size"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.view_details)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 500)
        self.table.setColumnWidth(4, 180)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 100)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(self.view_details)
        button_layout.addWidget(view_btn)
        
        pedigree_btn = QPushButton("View Pedigree")
        pedigree_btn.clicked.connect(self.view_pedigree)
        button_layout.addWidget(pedigree_btn)
        
        add_btn = QPushButton("Add Cat")
        add_btn.clicked.connect(self.add_cat)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Cat")
        edit_btn.clicked.connect(self.edit_cat)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Cat")
        delete_btn.clicked.connect(self.delete_cat)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def refresh_table(self):
        """Refresh the table with all cats"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        registry = self.main_window.registry
        phenotype_calc = self.main_window.phenotype_calculator
        
        for cat in sorted(registry.cats.values(), key=lambda c: c.id):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(cat.id)))
            self.table.setItem(row, 1, QTableWidgetItem(cat.name))
            self.table.setItem(row, 2, QTableWidgetItem(cat.sex.capitalize()))
            self.table.setItem(row, 3, QTableWidgetItem(phenotype_calc.calculate_phenotype(cat)))
            self.table.setItem(row, 4, QTableWidgetItem(phenotype_calc.calculate_eye_color(cat)))
            self.table.setItem(row, 5, QTableWidgetItem(cat.get_build_phenotype()))
            self.table.setItem(row, 6, QTableWidgetItem(cat.get_size_phenotype()))
        
        self.table.setSortingEnabled(True)
        self.update_results_label()
        self.main_window.update_statusbar()
    
    def apply_filters(self):
        """Apply search and filter criteria"""
        search_text = self.search_input.text().lower()
        sex_filter = self.sex_filter.currentText()
        fur_filter = self.fur_filter.currentText()
        
        registry = self.main_window.registry
        phenotype_calc = self.main_window.phenotype_calculator
        
        for row in range(self.table.rowCount()):
            cat_id = int(self.table.item(row, 0).text())
            cat = registry.get_cat(cat_id)
            
            show = True
            
            # Text search
            if search_text:
                searchable = f"{cat.id} {cat.name} {phenotype_calc.calculate_phenotype(cat)}".lower()
                if search_text not in searchable:
                    show = False
            
            # Sex filter
            if show and sex_filter != "All":
                if cat.sex.capitalize() != sex_filter:
                    show = False
            
            # Fur filter
            if show and fur_filter != "All":
                phenotype = phenotype_calc.calculate_phenotype(cat)
                if fur_filter not in phenotype:
                    show = False
            
            # Parent filter
            if show and self.has_parents.isChecked():
                if not cat.sire_id and not cat.dam_id:
                    show = False
            
            # Offspring filter
            if show and self.has_offspring.isChecked():
                offspring = registry.get_offspring(cat.id)
                if not offspring:
                    show = False
            
            self.table.setRowHidden(row, not show)
        
        self.update_results_label()
    
    def update_results_label(self):
        """Update the results count label"""
        total = self.table.rowCount()
        visible = sum(1 for row in range(total) if not self.table.isRowHidden(row))
        self.results_label.setText(f"Showing {visible} of {total} cats")
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.sex_filter.setCurrentIndex(0)
        self.fur_filter.setCurrentIndex(0)
        self.has_parents.setChecked(False)
        self.has_offspring.setChecked(False)
    
    def get_selected_cat_id(self):
        """Get the ID of the currently selected cat"""
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        return int(self.table.item(row, 0).text())
    
    
    def view_details(self):
        """View detailed information about selected cat"""
        cat_id = self.get_selected_cat_id()
        if cat_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a cat first.")
            return
        
        cat = self.main_window.registry.get_cat(cat_id)
        from ui.dialogs.cat_details_dialog import CatDetailsDialog
        dialog = CatDetailsDialog(cat, self.main_window, self)
        dialog.exec()
    
    def view_pedigree(self):
        """View pedigree of selected cat"""
        cat_id = self.get_selected_cat_id()
        if cat_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a cat first.")
            return
        
        cat = self.main_window.registry.get_cat(cat_id)
        dialog = PedigreeDialog(cat, self.main_window, self)
        dialog.exec()
    
    def add_cat(self):
        """Add a new cat"""
        dialog = CatEditorDialog(None, self.main_window, self)
        if dialog.exec():
            self.refresh_table()
    
    def edit_cat(self):
        """Edit selected cat"""
        cat_id = self.get_selected_cat_id()
        if cat_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a cat first.")
            return
        
        cat = self.main_window.registry.get_cat(cat_id)
        dialog = CatEditorDialog(cat, self.main_window, self)
        if dialog.exec():
            self.refresh_table()
    
    def delete_cat(self):
        """Delete selected cat"""
        cat_id = self.get_selected_cat_id()
        if cat_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a cat first.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete Cat #{cat_id}? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.main_window.registry.remove_cat(cat_id)
            self.refresh_table()