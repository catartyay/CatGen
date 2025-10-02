"""
Generation tab - randomly generate cats
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from core.cat import Cat
import random
from datetime import datetime


class GenerationTab(QWidget):
    """Random cat generation interface"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_cat = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the generation interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Random Cat Generation")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Info text
        info = QLabel(
            "Generate random cats with natural genetic distributions."
        )
        info.setWordWrap(True)
        info.setStyleSheet("padding: 10px; color: #666;")
        layout.addWidget(info)
        
        # Generation button
        button_group = QGroupBox("Generate Cat")
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Random Cat")
        generate_btn.setMinimumHeight(60)
        generate_btn.setMinimumWidth(300)
        generate_btn.clicked.connect(self.generate_cat)
        button_layout.addStretch()
        button_layout.addWidget(generate_btn)
        button_layout.addStretch()
        
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # Preview area
        preview_group = QGroupBox("Generated Cat")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(400)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Save button
        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save to Registry")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_cat)
        save_layout.addWidget(self.save_btn)
        save_layout.addStretch()
        layout.addLayout(save_layout)
    
    def generate_cat(self):
        """Generate a random cat"""
        try:
            genetics = self.main_window.genetics_engine
            
            # Create new cat
            sex = random.choice(['male', 'female'])
            cat = Cat(sex=sex)
            
            # Generate random genes
            cat.genes = self.generate_random_genes(sex)
            
            self.current_cat = cat
            self.display_cat_preview(cat)
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Generation Error",
                f"Failed to generate cat:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()
    
    def generate_random_genes(self, sex: str) -> dict:
        """Generate random genetic makeup"""
        genes = {}
        genetics = self.main_window.genetics_engine
        
        for gene_name, gene_data in genetics.genes.items():
            alleles = gene_data['alleles']
            weights = [gene_data['weights'].get(a, 1) for a in alleles]
            
            # Check if X-linked
            is_x_linked = gene_data.get('x_linked', False)
            
            if is_x_linked and sex == 'male':
                # Males only get one X chromosome
                genes[gene_name] = [random.choices(alleles, weights=weights)[0]]
            else:
                # Two alleles
                a1 = random.choices(alleles, weights=weights)[0]
                a2 = random.choices(alleles, weights=weights)[0]
                genes[gene_name] = [a1, a2]
        
        return genes
    
    def display_cat_preview(self, cat: Cat):
        """Display generated cat information"""
        phenotype_calc = self.main_window.phenotype_calculator
        
        text = f"GENERATED CAT\n"
        text += f"{'=' * 70}\n\n"
        text += f"Sex: {cat.sex.capitalize()}\n\n"
        text += f"PHENOTYPE:\n"
        text += f"{'-' * 70}\n"
        text += f"{phenotype_calc.calculate_phenotype(cat)}\n"
        text += f"Eye Color: {phenotype_calc.calculate_eye_color(cat)}\n"
        text += f"White Markings: {phenotype_calc.get_white_percentage(cat)}%\n"
        text += f"Build: {cat.get_build_phenotype()}\n"
        text += f"Size: {cat.get_size_phenotype()}\n\n"
        text += f"GENOTYPE:\n"
        text += f"{'-' * 70}\n"
        
        genetics = self.main_window.genetics_engine
        for gene_name, alleles in sorted(cat.genes.items()):
            gene_info = genetics.get_gene_info(gene_name)
            if gene_info:
                display_name = gene_info['name']
                if len(alleles) == 1:
                    desc = genetics.get_allele_description(gene_name, alleles[0])
                    text += f"{display_name}: {alleles[0]} ({desc})\n"
                else:
                    # Sort by dominance (highest first)
                    dom = gene_info.get('dominance', {})
                    sorted_alleles = sorted(alleles, 
                                          key=lambda a: dom.get(a, 0), 
                                          reverse=True)
                    desc1 = genetics.get_allele_description(gene_name, sorted_alleles[0])
                    desc2 = genetics.get_allele_description(gene_name, sorted_alleles[1])
                    text += f"{display_name}: {sorted_alleles[0]}/{sorted_alleles[1]} ({desc1}/{desc2})\n"
        
        self.preview_text.setPlainText(text)
    
    def save_cat(self):
        """Save the generated cat to the registry"""
        if not self.current_cat:
            return
        
        # Set birth date
        self.current_cat.birth_date = datetime.now().strftime('%Y-%m-%d')
        
        # Add to registry
        cat_id = self.main_window.registry.add_cat(self.current_cat)
        
        # Clear preview
        self.preview_text.append(f"\n{'=' * 70}\n")
        self.preview_text.append(f"✓ Cat #{cat_id} saved to registry!\n")
        
        self.save_btn.setEnabled(False)
        self.current_cat = None
        
        # Refresh registry tab
        self.main_window.registry_tab.refresh_table()
        
        QMessageBox.information(
            self,
            "Cat Saved",
            f"Cat #{cat_id} has been added to the registry!"
        )