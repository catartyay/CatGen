"""
Breeding tab - interface for breeding cats and viewing litter results
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QSpinBox, QTextEdit,
                               QGroupBox, QMessageBox, QDoubleSpinBox)
from PySide6.QtCore import Qt
from datetime import datetime


class BreedingTab(QWidget):
    """Breeding interface"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pending_litter = []
        self.setup_ui()
    
    def setup_ui(self):
        """Create the breeding interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Breed Cats")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Parent selection
        parent_group = QGroupBox("Select Parents")
        parent_layout = QVBoxLayout()
        
        # Sire selection
        sire_layout = QHBoxLayout()
        sire_layout.addWidget(QLabel("Sire (Male):"))
        self.sire_combo = QComboBox()
        self.sire_combo.setMinimumWidth(500)
        sire_layout.addWidget(self.sire_combo)
        sire_layout.addStretch()
        parent_layout.addLayout(sire_layout)
        
        # Dam selection
        dam_layout = QHBoxLayout()
        dam_layout.addWidget(QLabel("Dam (Female):"))
        self.dam_combo = QComboBox()
        self.dam_combo.setMinimumWidth(500)
        dam_layout.addWidget(self.dam_combo)
        dam_layout.addStretch()
        parent_layout.addLayout(dam_layout)
        
        parent_group.setLayout(parent_layout)
        layout.addWidget(parent_group)
        
       # Breeding parameters
        param_group = QGroupBox("Breeding Parameters")
        param_layout = QHBoxLayout()
        
        param_layout.addWidget(QLabel("Litter Size:"))
        self.litter_size = QSpinBox()
        self.litter_size.setRange(1, 12)
        self.litter_size.setValue(4)
        param_layout.addWidget(self.litter_size)
        
        param_layout.addStretch()
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Litter")
        generate_btn.clicked.connect(self.generate_litter)
        button_layout.addWidget(generate_btn)
        
        self.save_btn = QPushButton("Save Litter to Registry")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_litter)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Litter preview
        preview_group = QGroupBox("Litter Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(300)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
    
    def refresh_parent_lists(self):
        """Refresh the parent selection dropdowns"""
        registry = self.main_window.registry
        phenotype_calc = self.main_window.phenotype_calculator
        
        # Clear existing items
        self.sire_combo.clear()
        self.dam_combo.clear()
        
        # Get males and females
        males = registry.get_males()
        females = registry.get_females()
        
        # Populate sire combo
        for cat in sorted(males, key=lambda c: c.id):
            label = f"#{cat.id} - {cat.name if cat.name else 'Unnamed'} - {phenotype_calc.calculate_phenotype(cat)}"
            self.sire_combo.addItem(label, cat.id)
        
        # Populate dam combo
        for cat in sorted(females, key=lambda c: c.id):
            label = f"#{cat.id} - {cat.name if cat.name else 'Unnamed'} - {phenotype_calc.calculate_phenotype(cat)}"
            self.dam_combo.addItem(label, cat.id)
    
    def generate_litter(self):
        """Generate a litter from selected parents"""
        if self.sire_combo.count() == 0 or self.dam_combo.count() == 0:
            QMessageBox.warning(
                self,
                "No Parents Available",
                "You need at least one male and one female cat to breed."
            )
            return
        
        sire_id = self.sire_combo.currentData()
        dam_id = self.dam_combo.currentData()
        
        if sire_id is None or dam_id is None:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select both a sire and a dam."
            )
            return
        
        # Check for relatedness
        registry = self.main_window.registry
        breeding_engine = self.main_window.breeding_engine
        
        if breeding_engine.check_relatedness(sire_id, dam_id, registry.cats):
            reply = QMessageBox.question(
                self,
                "Related Cats",
                "These cats are related within 3 generations. Breed anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Get parents
        sire = registry.get_cat(sire_id)
        dam = registry.get_cat(dam_id)
        
        # Generate litter
        # Generate litter
        litter_size = self.litter_size.value()
        
        self.pending_litter = breeding_engine.breed_cats(
            sire, dam, litter_size, 1.0  
        )
        
        # Display preview
        self.display_litter_preview(sire, dam)
        self.save_btn.setEnabled(True)
    
    def display_litter_preview(self, sire, dam):
        """Display the generated litter in the preview area"""
        phenotype_calc = self.main_window.phenotype_calculator
        
        text = f"LITTER PREVIEW\n"
        text += f"{'=' * 80}\n\n"
        text += f"Sire: #{sire.id} - {sire.name if sire.name else 'Unnamed'}\n"
        text += f"      {phenotype_calc.calculate_phenotype(sire)}\n\n"
        text += f"Dam:  #{dam.id} - {dam.name if dam.name else 'Unnamed'}\n"
        text += f"      {phenotype_calc.calculate_phenotype(dam)}\n\n"
        text += f"Litter Size: {len(self.pending_litter)}\n"
        text += f"{'=' * 80}\n\n"
        
        for i, kitten in enumerate(self.pending_litter, 1):
            text += f"KITTEN #{i}\n"
            text += f"{'-' * 40}\n"
            text += f"Sex: {kitten.sex.capitalize()}\n"
            text += f"Phenotype: {phenotype_calc.calculate_phenotype(kitten)}\n"
            text += f"Eye Color: {phenotype_calc.calculate_eye_color(kitten)}\n"
            text += f"White: {phenotype_calc.get_white_percentage(kitten)}%\n"
            text += f"Build: {kitten.get_build_phenotype()}\n"
            text += f"Size: {kitten.get_size_phenotype()}\n"
            text += f"\nGenotype:\n"
            
            for gene_name, alleles in sorted(kitten.genes.items()):
                gene_info = self.main_window.genetics_engine.get_gene_info(gene_name)
                if gene_info:
                    display_name = gene_info['name']
                    if len(alleles) == 1:
                        text += f"  {display_name}: {alleles[0]}\n"
                    else:
                        text += f"  {display_name}: {alleles[0]}/{alleles[1]}\n"
            
            text += "\n"
        
        self.preview_text.setPlainText(text)
    
    def save_litter(self):
        """Save the pending litter to the registry"""
        if not self.pending_litter:
            return
        
        registry = self.main_window.registry
        
        # Add each kitten to registry
        for kitten in self.pending_litter:
            kitten.birth_date = datetime.now().strftime('%Y-%m-%d')
            registry.add_cat(kitten)
        
        count = len(self.pending_litter)
        self.pending_litter = []
        
        # Update UI
        self.save_btn.setEnabled(False)
        self.preview_text.append(f"\n{'=' * 80}\n")
        self.preview_text.append(f"✓ Saved {count} kitten(s) to registry!\n")
        
        # Refresh registry tab
        self.main_window.registry_tab.refresh_table()
        
        QMessageBox.information(
            self,
            "Litter Saved",
            f"{count} kitten(s) have been added to the registry!"
        )