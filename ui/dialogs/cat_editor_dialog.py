"""
Dialog for adding or editing cats
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QPushButton, QLabel, QLineEdit, QComboBox,
                               QScrollArea, QWidget, QGroupBox, QRadioButton,
                               QButtonGroup, QMessageBox)
from PySide6.QtCore import Qt
from core.cat import Cat
from datetime import datetime


class CatEditorDialog(QDialog):
    """Dialog for adding or editing a cat"""
    
    def __init__(self, cat, main_window, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.main_window = main_window
        self.is_edit = cat is not None
        
        title = f"Edit Cat #{cat.id}" if self.is_edit else "Add New Cat"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(900, 750)
        
        self.gene_selectors = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Create the dialog interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_text = f"Edit Cat #{self.cat.id}" if self.is_edit else "Add New Cat"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Scrollable area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Basic info group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        if self.cat:
            self.name_input.setText(self.cat.name)
        basic_layout.addRow("Name:", self.name_input)
        
        # Sex selection
        sex_widget = QWidget()
        sex_layout = QHBoxLayout()
        sex_layout.setContentsMargins(0, 0, 0, 0)
        self.sex_group = QButtonGroup()
        
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        self.sex_group.addButton(self.male_radio, 0)
        self.sex_group.addButton(self.female_radio, 1)
        
        if self.cat and self.cat.sex == 'male':
            self.male_radio.setChecked(True)
        else:
            self.female_radio.setChecked(True)
        
        sex_layout.addWidget(self.male_radio)
        sex_layout.addWidget(self.female_radio)
        sex_layout.addStretch()
        sex_widget.setLayout(sex_layout)
        basic_layout.addRow("Sex:", sex_widget)
        
        self.date_input = QLineEdit()
        if self.cat:
            self.date_input.setText(self.cat.birth_date)
        else:
            self.date_input.setText(datetime.now().strftime('%Y-%m-%d'))
        basic_layout.addRow("Birth Date:", self.date_input)
        
        self.sire_input = QLineEdit()
        if self.cat and self.cat.sire_id:
            self.sire_input.setText(str(self.cat.sire_id))
        basic_layout.addRow("Sire ID:", self.sire_input)
        
        self.dam_input = QLineEdit()
        if self.cat and self.cat.dam_id:
            self.dam_input.setText(str(self.cat.dam_id))
        basic_layout.addRow("Dam ID:", self.dam_input)
        
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)
        
        # Genetics group
        genes_group = QGroupBox("Genetics")
        genes_layout = QVBoxLayout()
        
        genetics = self.main_window.genetics_engine
        for gene_name, gene_data in genetics.genes.items():
            gene_widget = self.create_gene_selector(gene_name, gene_data)
            genes_layout.addWidget(gene_widget)
        
        genes_group.setLayout(genes_layout)
        scroll_layout.addWidget(genes_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_cat)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def create_gene_selector(self, gene_name, gene_data):
        """Create selector widget for a gene"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        widget.setLayout(layout)
        
        # Label
        label = QLabel(f"{gene_data['name']}:")
        label.setMinimumWidth(200)
        layout.addWidget(label)
        
        # Allele selectors
        alleles = gene_data['alleles']
        
        combo1 = QComboBox()
        combo1.addItems(alleles)
        layout.addWidget(combo1)
        
        combo2 = QComboBox()
        combo2.addItems(alleles)
        layout.addWidget(combo2)
        
        # Set current values if editing
        if self.cat and gene_name in self.cat.genes:
            cat_alleles = self.cat.genes[gene_name]
            if len(cat_alleles) >= 1:
                combo1.setCurrentText(cat_alleles[0])
            if len(cat_alleles) >= 2:
                combo2.setCurrentText(cat_alleles[1])
            
            # Hide second combo for X-linked males
            if gene_data.get('x_linked') and self.cat.sex == 'male':
                combo2.setVisible(False)
        
        self.gene_selectors[gene_name] = (combo1, combo2)
        layout.addStretch()
        
        return widget
    
    def save_cat(self):
        """Save the cat"""
        try:
            # Get sex
            sex = 'male' if self.male_radio.isChecked() else 'female'
            
            # Collect genes
            genes = {}
            genetics = self.main_window.genetics_engine
            
            for gene_name, (combo1, combo2) in self.gene_selectors.items():
                gene_data = genetics.get_gene_info(gene_name)
                
                if gene_data.get('x_linked') and sex == 'male':
                    genes[gene_name] = [combo1.currentText()]
                else:
                    genes[gene_name] = [combo1.currentText(), combo2.currentText()]
            
            # Get parent IDs
            sire_id = None
            dam_id = None
            
            if self.sire_input.text():
                try:
                    sire_id = int(self.sire_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Sire ID must be a number")
                    return
            
            if self.dam_input.text():
                try:
                    dam_id = int(self.dam_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Dam ID must be a number")
                    return
            
            if self.is_edit:
                # Update existing cat
                self.cat.name = self.name_input.text()
                self.cat.sex = sex
                self.cat.birth_date = self.date_input.text()
                self.cat.sire_id = sire_id
                self.cat.dam_id = dam_id
                self.cat.genes = genes
                self.cat.invalidate_cache()
            else:
                # Create new cat
                cat = Cat(
                    name=self.name_input.text(),
                    sex=sex,
                    genes=genes,
                    birth_date=self.date_input.text(),
                    sire_id=sire_id,
                    dam_id=dam_id
                )
                self.main_window.registry.add_cat(cat)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save cat:\n{str(e)}")