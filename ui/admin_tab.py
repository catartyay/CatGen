"""
Admin tab - gene configuration and management
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QMessageBox, QTextEdit, QDialog, QFormLayout,
                               QLineEdit, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt
import json


class AdminTab(QWidget):
    """Gene administration interface"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.refresh_gene_list()
    
    def setup_ui(self):
        """Create the admin interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Gene Administration")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Warning
        warning = QLabel(
            "⚠️ Caution: Modifying genes affects all cats. "
            "Changes take effect immediately and cannot be undone."
        )
        warning.setStyleSheet("color: #d32f2f; padding: 10px; background-color: #ffebee; border-radius: 4px;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        # Gene table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Gene ID", "Display Name", "Alleles", "X-Linked"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 400)
        self.table.setColumnWidth(3, 100)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("View/Edit Gene")
        view_btn.clicked.connect(self.edit_gene)
        button_layout.addWidget(view_btn)
        
        add_btn = QPushButton("Add Gene")
        add_btn.clicked.connect(self.add_gene)
        button_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("Delete Gene")
        delete_btn.clicked.connect(self.delete_gene)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Changes to File")
        save_btn.setStyleSheet("background-color: #2196F3;")
        save_btn.clicked.connect(self.save_genes)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_gene_list(self):
        """Refresh the gene table"""
        self.table.setRowCount(0)
        
        genetics = self.main_window.genetics_engine
        
        for gene_id, gene_data in genetics.genes.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(gene_id))
            self.table.setItem(row, 1, QTableWidgetItem(gene_data.get('name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(', '.join(gene_data.get('alleles', []))))
            self.table.setItem(row, 3, QTableWidgetItem('Yes' if gene_data.get('x_linked') else 'No'))
    
    def get_selected_gene_id(self):
        """Get the ID of the selected gene"""
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        return self.table.item(row, 0).text()
    
    def edit_gene(self):
        """Edit the selected gene"""
        gene_id = self.get_selected_gene_id()
        if not gene_id:
            QMessageBox.warning(self, "No Selection", "Please select a gene first.")
            return
        
        genetics = self.main_window.genetics_engine
        gene_data = genetics.get_gene_info(gene_id)
        
        dialog = GeneEditorDialog(gene_id, gene_data, self)
        if dialog.exec():
            genetics.update_gene(gene_id, dialog.get_gene_data())
            self.refresh_gene_list()
            QMessageBox.information(self, "Success", "Gene updated successfully!")
    
    def add_gene(self):
        """Add a new gene"""
        dialog = GeneEditorDialog(None, None, self)
        if dialog.exec():
            gene_id, gene_data = dialog.get_gene_data_with_id()
            
            genetics = self.main_window.genetics_engine
            if gene_id in genetics.genes:
                QMessageBox.warning(self, "Duplicate ID", "A gene with this ID already exists!")
                return
            
            genetics.add_gene(gene_id, gene_data)
            self.refresh_gene_list()
            QMessageBox.information(self, "Success", "Gene added successfully!")
    
    def delete_gene(self):
        """Delete the selected gene"""
        gene_id = self.get_selected_gene_id()
        if not gene_id:
            QMessageBox.warning(self, "No Selection", "Please select a gene first.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete gene '{gene_id}'? This cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.main_window.genetics_engine.remove_gene(gene_id)
            self.refresh_gene_list()
            QMessageBox.information(self, "Deleted", "Gene deleted successfully!")
    
    def save_genes(self):
        """Save gene configuration to file"""
        try:
            self.main_window.genetics_engine.save_genes()
            QMessageBox.information(self, "Saved", "Gene configuration saved to genes.json!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")


class GeneEditorDialog(QDialog):
    """Dialog for editing gene definitions"""
    
    def __init__(self, gene_id, gene_data, parent=None):
        super().__init__(parent)
        self.gene_id = gene_id
        self.is_new = gene_data is None
        
        if self.is_new:
            self.gene_data = {
                'name': '',
                'alleles': [],
                'descriptions': {},
                'dominance': {},
                'weights': {},
                'x_linked': False
            }
        else:
            self.gene_data = gene_data.copy()
        
        self.setWindowTitle("Edit Gene" if gene_id else "Add Gene")
        self.setModal(True)
        self.resize(700, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Create dialog interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Basic info
        info_group = QGroupBox("Basic Information")
        info_layout = QFormLayout()
        
        if self.is_new:
            self.id_input = QLineEdit()
            info_layout.addRow("Gene ID:", self.id_input)
        
        self.name_input = QLineEdit(self.gene_data.get('name', ''))
        info_layout.addRow("Display Name:", self.name_input)
        
        self.x_linked = QCheckBox()
        self.x_linked.setChecked(self.gene_data.get('x_linked', False))
        info_layout.addRow("X-Linked:", self.x_linked)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # JSON data
        json_group = QGroupBox("Gene Data (JSON Format)")
        json_layout = QVBoxLayout()
        
        self.json_edit = QTextEdit()
        self.json_edit.setPlainText(json.dumps(self.gene_data, indent=2))
        json_layout.addWidget(self.json_edit)
        
        json_group.setLayout(json_layout)
        layout.addWidget(json_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def save(self):
        """Validate and save gene data"""
        try:
            # Parse JSON
            gene_data = json.loads(self.json_edit.toPlainText())
            
            # Update basic fields
            gene_data['name'] = self.name_input.text()
            gene_data['x_linked'] = self.x_linked.isChecked()
            
            # Validate required fields
            if not gene_data.get('name'):
                raise ValueError("Display name is required")
            if not gene_data.get('alleles'):
                raise ValueError("At least one allele is required")
            
            self.gene_data = gene_data
            self.accept()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Error", f"Invalid JSON format:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Validation failed:\n{str(e)}")
    
    def get_gene_data(self):
        """Get gene data"""
        return self.gene_data
    
    def get_gene_data_with_id(self):
        """Get gene ID and data (for new genes)"""
        if self.is_new:
            return self.id_input.text(), self.gene_data
        return self.gene_id, self.gene_data