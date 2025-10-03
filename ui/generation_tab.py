"""
Generation Tab - Clean, simple, and functional
Replace: ui/generation_tab.py
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QGroupBox, QMessageBox, QFrame)
from PySide6.QtCore import Qt
from core.cat import Cat
import random
from datetime import datetime


class GenerationTab(QWidget):
    """Simple, clean random cat generation interface"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_cat = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create clean interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("🎲 Random Cat Generator")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Description
        info = QLabel("Generate random cats with realistic genetic distributions")
        info.setStyleSheet("color: #666; padding: 10px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Generate section
        gen_group = QGroupBox("Generate Cat")
        gen_layout = QVBoxLayout()
        
        self.generate_btn = QPushButton("Generate Random Cat")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_cat)
        gen_layout.addWidget(self.generate_btn)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # Preview area
        preview_group = QGroupBox("Generated Cat")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(400)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New';
            }
        """)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save to Registry")
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 0 20px;
            }
            QPushButton:hover:enabled {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.save_btn.clicked.connect(self.save_cat)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
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
    
    def generate_random_genes(self, sex: str) -> dict:
        """Generate random genetic makeup"""
        genes = {}
        genetics = self.main_window.genetics_engine
        
        for gene_name, gene_data in genetics.genes.items():
            alleles = gene_data['alleles']
            weights = [gene_data['weights'].get(a, 1) for a in alleles]
            
            is_x_linked = gene_data.get('x_linked', False)
            
            if is_x_linked and sex == 'male':
                genes[gene_name] = [random.choices(alleles, weights=weights)[0]]
            else:
                a1 = random.choices(alleles, weights=weights)[0]
                a2 = random.choices(alleles, weights=weights)[0]
                genes[gene_name] = [a1, a2]
        
        return genes
    
    def display_cat_preview(self, cat: Cat):
        """Display generated cat information"""
        phenotype_calc = self.main_window.phenotype_calculator
        
        text = "=" * 80 + "\n"
        text += "  GENERATED CAT\n"
        text += "=" * 80 + "\n\n"
        
        text += f"Sex: {cat.sex.upper()}\n\n"
        
        # Appearance
        text += "APPEARANCE:\n"
        text += "-" * 80 + "\n"
        phenotype = phenotype_calc.calculate_phenotype(cat)
        text += f"Phenotype: {phenotype}\n"
        text += f"Eye Color: {phenotype_calc.calculate_eye_color(cat)}\n"
        text += f"White Markings: {phenotype_calc.get_white_percentage(cat)}%\n"
        text += f"Build: {cat.get_build_phenotype()} ({cat.build_value}/100)\n"
        text += f"Size: {cat.get_size_phenotype()} ({cat.size_value}/100)\n\n"
        
        # Genetics
        text += "GENETICS:\n"
        text += "-" * 80 + "\n"
        
        genetics = self.main_window.genetics_engine
        for gene_name, alleles in sorted(cat.genes.items()):
            gene_info = genetics.get_gene_info(gene_name)
            if gene_info:
                display_name = gene_info['name']
                
                if len(alleles) == 1:
                    desc = genetics.get_allele_description(gene_name, alleles[0])
                    text += f"{display_name:20} {alleles[0]:8} ({desc})\n"
                else:
                    dom = gene_info.get('dominance', {})
                    sorted_alleles = sorted(alleles, key=lambda a: dom.get(a, 0), reverse=True)
                    desc1 = genetics.get_allele_description(gene_name, sorted_alleles[0])
                    desc2 = genetics.get_allele_description(gene_name, sorted_alleles[1])
                    text += f"{display_name:20} {sorted_alleles[0]}/{sorted_alleles[1]:8} ({desc1}, {desc2})\n"
        
        text += "\n" + "=" * 80 + "\n"
        text += "✓ Ready to save to registry!\n"
        text += "=" * 80 + "\n"
        
        self.preview_text.setPlainText(text)
    
    def save_cat(self):
        """Save the generated cat to the registry"""
        if not self.current_cat:
            return
        
        self.current_cat.birth_date = datetime.now().strftime('%Y-%m-%d')
        cat_id = self.main_window.registry.add_cat(self.current_cat)
        
        self.preview_text.append(f"\n{'=' * 80}\n")
        self.preview_text.append(f"✓ Cat #{cat_id} saved to registry!\n")
        self.preview_text.append(f"{'=' * 80}\n")
        
        self.save_btn.setEnabled(False)
        self.current_cat = None
        
        # Refresh registry tab
        self.main_window.registry_tab.refresh_table()
        
        QMessageBox.information(
            self,
            "Cat Saved",
            f"Cat #{cat_id} has been added to the registry!"
        )